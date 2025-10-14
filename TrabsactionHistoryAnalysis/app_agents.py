# app_agents.py

import os
import glob
import base64
import re
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage, HumanMessage
from langchain_google_vertexai import ChatVertexAI
from langchain_experimental.tools import PythonREPLTool
from langchain_community.agent_toolkits import FileManagementToolkit

from agent_tools import get_analyst_tools, get_statistician_tools
from graph_builder import create_agent_workflow
from rag_agent import RAGAgent
import config

def summarize_tool_output(output: str, max_length: int = 1500) -> str:
    """Truncates the output of a tool to prevent prompt poisoning."""
    if len(output) > max_length:
        truncated_output = output[:max_length]
        # Try to find the last newline to avoid cutting a line in the middle
        last_newline = truncated_output.rfind('\n')
        if last_newline != -1:
            truncated_output = truncated_output[:last_newline]
        return truncated_output + "\n\n... [Output truncated for brevity] ..."
    return output

class AppAgentOrchestrator:
    """A modified AgentOrchestrator that yields events for a Streamlit app."""
    def __init__(self):
        self.llm = ChatVertexAI(project=config.PROJECT_ID, model_name=config.MODEL_NAME)
        self.senior_agent = self.llm
        self.statistician_planner_agent = self.llm
        self.finalizer_agent = self.llm
        self.rag_agent = RAGAgent()
        statistician_reporter_tools = get_statistician_tools()
        self.statistician_reporter_agent = create_agent_workflow(self.llm, statistician_reporter_tools)

    def run_statistician_analyst_loop(self, high_level_directive: str, cycle_num: int, previous_report_content: str):
        """
        Runs the iterative sub-workflow between the Statistician and the Analyst,
        now with a self-correcting Analyst that retries N times.
        """
        yield {"type": "system", "author": "System", "content": f"🔬 Kicking off Statistician & Analyst Sub-Workflow (Cycle {cycle_num})"}
        
        conversation_history = []
        structured_log = []
        supplemental_rag_context = "No context retrieved yet. This is the first turn."
        
        for i in range(7):
            yield {"type": "system", "author": "System", "content": f"🔄 Inner Cycle {i + 1}/7"}

            try:
                directory_listing = os.listdir("output")
            except FileNotFoundError:
                directory_listing = []
            
            history_so_far = ""
            for msg in conversation_history:
                if isinstance(msg, AIMessage):
                    history_so_far += f"\n**Your Last Turn (Reasoning & Directive):**\n{msg.content}"
                elif isinstance(msg, HumanMessage):
                    content_text = msg.content[0]['text'] if isinstance(msg.content, list) else str(msg.content)
                    history_so_far += f"\n**Analyst's Last Output:**\n{content_text}"

            full_context = (
                f"**High-Level Directive for this Cycle:**\n{high_level_directive}\n\n"
                f"**Previous Cycle's Report (for context and schema reference):**\n{previous_report_content}\n\n"
                f"**Current Contents of `output` Directory (Your Long-Term Memory):**\n{directory_listing}\n\n"
                f"**Supplemental Context from Bayesian Analysis Textbook:**\n{supplemental_rag_context}\n\n"
                f"**Session History So Far (Inner Loop):**\n{history_so_far}"
            )
            
            yield {"type": "system", "author": "System", "content": "🧠 Bayesian Data Scientist is reasoning..."}

            statistician_system_prompt = SystemMessage(
                content="""You are a meticulous Principal Bayesian Data Scientist working for the **Render B2B lending platform**.
                Your goal is to analyze financial data by forming a plan (Reasoning) and then writing Python code (Directive) to execute that plan.

                ## Core Memory
                Your most important source of memory is the 'Previous Cycle's Report'. It contains a `## Data Schema Handover` section that provides the ground truth for all available datasets and their exact column names. You MUST use this to avoid `KeyError` exceptions.

                ## Critical Instructions
                1.  **Schema Adherence:** You MUST use the exact column names found in the `Data Schema Handover` of the previous report.
                2.  **File Paths:** All file paths MUST be relative and start with `output/`. NEVER use a leading slash.
                3.  **Plotting:** Any directive that generates a plot MUST begin with the `matplotlib.use('Agg')` code block.
                4.  **Output Handling:** Your Python code should NOT print large DataFrames. It should perform its task and print a single, simple confirmation message at the end.

                ## YOUR TASK
                Review all the context provided (High-level directive, previous report, file listing, etc.). Based on this, you must formulate your reasoning and then provide the next Python directive. Your response MUST strictly follow the format below. Do not add any other text before or after this structure.

                ```markdown
                ## Reasoning
                
                1.  **Review of Previous Report & Schema:** (Start by acknowledging the data schemas from the last report to ground your plan.)
                2.  **State Your Priors:** (State your belief *before* executing the new directive.)
                3.  **Gather Evidence (The Directive Plan):** (Describe the goal of the Python code you are about to write.)
                4.  **Articulate Your Posterior Belief:** (Describe how the evidence you plan to gather will update your beliefs in the *next* turn.)

                ## Directive
                
                ```python
                # Your Python code goes here.
                # It must follow all critical instructions.
                # 1. LOAD STATE (if necessary)
                # 2. EXECUTE LOGIC
                # 3. SAVE STATE
                ```
                ```
                """
            )
            
            messages_for_planner = [statistician_system_prompt, HumanMessage(content=full_context)]
            if conversation_history and isinstance(conversation_history[-1], HumanMessage):
                messages_for_planner.append(conversation_history[-1])

            statistician_response = self.statistician_planner_agent.invoke(messages_for_planner)
            statistician_response_text = str(statistician_response.content)

            reasoning, directive = "Could not parse.", ""
            code_block_match = re.search(r"```python\n(.*?)```", statistician_response_text, re.DOTALL)
            if code_block_match:
                directive = code_block_match.group(1).strip()
                reasoning_text = statistician_response_text[:code_block_match.start()]
                reasoning = re.sub(r"(?i)##\s*.*Reasoning.*|##\s*Directive", "", reasoning_text).strip() or "Reasoning section was empty."
            else:
                reasoning = statistician_response_text.strip()
            if not directive:
                reasoning += "\n\n**CRITICAL ERROR:** No valid Python code block (` ```python...``` `) was found."
            
            yield {"type": "reasoning", "author": "Statistician", "content": reasoning}
            if directive:
                yield {"type": "directive", "author": "Statistician", "content": directive}
            
            conversation_history.append(AIMessage(content=statistician_response_text))
            
            if not directive:
                yield {"type": "system", "author": "System", "content": "⚠️ Skipping analyst execution due to missing directive."}
                continue

            # <<< --- START OF NEW HYPERPARAMETER-DRIVEN CORRECTION LOOP --- >>>

            analyst_tool_output = ""
            files_before = set(os.listdir("output")) if os.path.exists("output") else set()
            code_to_execute = directive # Start with the original code

            for attempt in range(config.MAX_CORRECTION_ATTEMPTS):
                yield {"type": "system", "author": "System", "content": f"🛠️ Analyst attempt {attempt + 1}/{config.MAX_CORRECTION_ATTEMPTS} to execute..."}
                try:
                    # Execute the current version of the code
                    stateless_repl = PythonREPLTool()
                    analyst_tool_output = stateless_repl.invoke(code_to_execute)
                    
                    if "Traceback" not in analyst_tool_output and "Error" not in analyst_tool_output:
                        yield {"type": "system", "author": "System", "content": f"✅ Execution successful on attempt {attempt + 1}."}
                        break # Success! Exit the correction loop.
                    else:
                        raise Exception(analyst_tool_output)

                except Exception as e:
                    error_message = str(e)
                    yield {"type": "system", "author": "System", "content": f"⚠️ Attempt {attempt + 1} failed."}
                    yield {"type": "analyst_output", "author": "Analyst", "content": error_message}
                    
                    if attempt == config.MAX_CORRECTION_ATTEMPTS - 1:
                        yield {"type": "system", "author": "System", "content": f"❌ Self-correction failed after {config.MAX_CORRECTION_ATTEMPTS} attempts."}
                        analyst_tool_output = f"Final Error after {config.MAX_CORRECTION_ATTEMPTS} attempts:\n{error_message}"
                        break

                    yield {"type": "system", "author": "System", "content": "🧠 Analyst will attempt to self-correct..."}
                    debugger_prompt = SystemMessage(
                        content="""You are a senior Python debugger... [Full debugger prompt]"""
                    )
                    correction_context = (
                        f"Here is the script that failed:\n```python\n{code_to_execute}\n```\n\n"
                        f"Here is the error that it produced:\n```\n{error_message}\n```\n\n"
                        "Please provide the corrected Python code."
                    )
                    
                    corrected_code_response = self.llm.invoke([debugger_prompt, HumanMessage(content=correction_context)])
                    corrected_code = str(corrected_code_response.content).strip().strip('```python').strip('```').strip()
                    
                    yield {"type": "reasoning", "author": "Analyst", "content": f"**Correction Attempt:**\n\nThe previous code failed. I have corrected it and will now re-attempt execution."}
                    yield {"type": "directive", "author": "Analyst", "content": corrected_code}
                    
                    code_to_execute = corrected_code

            # <<< --- END OF NEW HYPERPARAMETER-DRIVEN CORRECTION LOOP --- >>>

            summarized_analyst_output = summarize_tool_output(analyst_tool_output)

            files_after = set(os.listdir("output")) if os.path.exists("output") else set()
            new_files = files_after - files_before
            generated_plots = [f"output/{fname}" for fname in new_files if fname.endswith(('.png', '.jpg', '.jpeg'))]
            
            yield {"type": "analyst_output", "author": "Analyst", "content": analyst_tool_output}
            for plot_path in generated_plots:
                yield {"type": "attachment", "author": "Analyst", "content": f"Generated plot: `{os.path.basename(plot_path)}`", "path": plot_path}
            
            structured_log.append({ "directive": directive, "result": analyst_tool_output, "plots": generated_plots })
            analyst_summary_for_stat = f"Task complete. Output summary:\n{summarized_analyst_output}"
            conversation_history.append(HumanMessage(content=[{"type": "text", "text": analyst_summary_for_stat}]))
        
        yield {"type": "system", "author": "System", "content": "✍️  Statistician is writing the cycle report..."}
        
        all_figures_this_cycle = sorted(list(set(p for entry in structured_log for p in entry['plots'])))

        log_as_string = ""
        for i_log, entry in enumerate(structured_log):
            log_as_string += f"### Turn {i_log+1}\n\n**Directive:**\n```python\n{entry['directive']}\n```\n\n**Result:**\n```text\n{entry['result']}\n```\n"
            if entry['plots']:
                log_as_string += "**Plots Generated in this Turn:**\n" + "\n".join([f"- `{path}`" for path in entry['plots']]) + "\n\n"
        
        summary_prompt = (
            "You are the Statistician Reporter AI, a meticulous chronicler of the analysis performed by your counterpart, the Bayesian Data Scientist."
            "\n\nYour audience is twofold: your AI supervisor (the Senior Director) and the next iteration of the Bayesian Data Scientist who will begin the next work cycle. Your report must therefore be both a high-level summary and a detailed technical handover."
            "\n\n## Core Directive: Document, Analyze, and Save"
            "\nYour single most important task is to create a markdown report that meticulously documents the events of the last work cycle and save it using the `write_file` tool. **You MUST ALWAYS generate a report and call the `write_file` tool, no matter the outcome.**"
            "\n\n## Report Generation Protocol"
            "\nReview the structured logs and available figures. Your report's content depends entirely on the outcome of the cycle."
            "\n\n### A. If the Cycle was Successful:"
            "\n1.  **Synthesize Findings:** Interpret the results and explain what the new evidence implies about the applicant's financial health."
            "\n2.  **Connect to Priors:** Mention how the evidence confirmed or updated the Bayesian Data Scientist's prior beliefs."
            "\n3.  **State Remaining Uncertainty:** Highlight what questions remain unanswered to set the stage for the next cycle."
            "\n\n### B. If the Cycle Encountered Errors or Failed:"
            "\nYour role becomes that of a forensic analyst. You MUST perform the following **Meticulous Failure Analysis**:"
            "\n1.  **Identify the Exact Error:** State the specific error message and the directive that caused it."
            "\n2.  **Trace the Causal Chain:** Describe the sequence of events that led to the failure."
            "\n3.  **Diagnose the Root Cause:** Reason about the *why* (e.g., flaw in code logic, environmental issue, flawed assumption)."
            "\n4.  **Propose a Corrective Action Plan:** Provide clear, actionable recommendations for the next cycle, including strategic pivots or debugging steps if necessary."
            "\n\n## Mandatory Technical Instructions"
            "\n1.  **Embed All Figures (CRITICAL GROUNDING RULE):** You will be given a list titled 'Figures Available for this Report'. This list is the **single source of truth** for which plots exist. You MUST ONLY embed figures whose exact filenames appear in this list. DO NOT invent, assume, or reference any figure that is not explicitly in the list, even if the logs suggest it was attempted. Hallucinating a file path for a non-existent figure is a critical failure."
            "\n    * **Correct format:** `![Caption](/output/figure.name.png)` (with a leading slash)"
            "\n    * **Incorrect format:** `![Caption](output/figure.name.png)` (without a leading slash)"
            "\n2.  **Final Action:** Your final action MUST be a call to the `write_file` tool to save your completed markdown report."
        )
        figures_list_str = "\n".join([f"- `{path}`" for path in all_figures_this_cycle])
        summary_input = f"Create a report based on these logs.\n\n**Figures:**\n{figures_list_str}\n\n**LOGS:**\n{log_as_string}"
        report_filename = f"intermediate_report_cycle_{cycle_num}.md"
        final_prompt_for_stat = f"{summary_input}\n\nSave the report to '{report_filename}'."
        stat_inputs = {"messages": [("system", summary_prompt), ("user", final_prompt_for_stat)]}
        self.statistician_reporter_agent.invoke(stat_inputs)
        
        report_path = f"output/{report_filename}"
        if os.path.exists(report_path):
            with open(report_path, "r", encoding='utf-8') as f:
                report_content = f.read()
            yield {"type": "attachment", "author": "Statistician", "content": f"Generated report: `{os.path.basename(report_path)}`", "path": report_path}
            return report_content, all_figures_this_cycle
        else:
            return "Error: Failed to produce a report.", []

    def run(self, local_csv_path: str):
        yield {"type": "system", "author": "System", "content": "🎬 Kicking off the Main Workflow..."}
        
        safe_local_path = local_csv_path.replace('\\', '/')
        next_directive_for_statistician = f"Begin the credit risk assessment of 'Artisan Digital'. Start with a high-level EDA of the dataset at '{safe_local_path}' and save a parquet checkpoint."
        
        all_generated_plots = []
        # MODIFICATION: Initialize a variable to hold the report content
        report_from_previous_cycle = "This is the first cycle. No previous report exists."

        for i in range(1, 6):
            yield {"type": "system", "author": "System", "content": f"👑 Outer Cycle {i}/5"}
            
            # MODIFICATION: Pass the previous report into the loop and capture the new one
            report_from_statistician, figures_from_last_cycle = yield from self.run_statistician_analyst_loop(
                next_directive_for_statistician, i, report_from_previous_cycle
            )
            
            # MODIFICATION: Update the variable for the next loop
            report_from_previous_cycle = report_from_statistician

            if figures_from_last_cycle:
                all_generated_plots.extend(figures_from_last_cycle)

            if i < 5:
                yield {"type": "system", "author": "System", "content": "🧠 Senior Analyst is reviewing the report..."}
                
                senior_input_message = HumanMessage(content=report_from_statistician)
                senior_reasoning_prompt = SystemMessage(
                    content="""You are the **Lead Credit Risk Analyst for the Render B2B Platform**, Abound's AI-driven decisioning engine. You are the strategic mind orchestrating a sophisticated, iterative financial analysis.

                    ## Strategic Mandate and Philosophy
                    Your purpose is to prove that a deep analysis of Open Banking data can uncover an applicant's **"forward-looking potential"**, moving beyond the limitations of a simple credit score. Your work must construct a comprehensive picture of their creditworthiness for our partner, **'EuroFin Bank'**.

                    ## The Iterative Analysis Framework
                    You guide your team through a structured, multi-stage review process. Each cycle must build logically upon the findings of the last. Your role is to ensure this progression is intelligent, efficient, and relentlessly focused on the final objective.

                    ## Your Core Task in Each Cycle
                    At the beginning of each cycle, you will be presented with the latest intermediate report. You MUST analyze this new information and then articulate your strategic reasoning by following and writing out these steps in exhaustive detail:

                    **0.  Review Data Schema Handover (CRITICAL FIRST STEP):**
                        * Before all else, locate the `## Data Schema Handover` section in the latest report. This section is your **ground truth** for the current state of all datasets.
                        * Explicitly list the key datasets and their column names in your reasoning.
                        * Your next directive MUST use the exact column names documented here to prevent `KeyError` exceptions.

                    **1.  Assess Progress Towards a Recommendation for EuroFin Bank:**
                        * Synthesize the most critical, business-relevant insights from the report. Interpret them.
                        * How does this new information impact your assessment of the applicant's risk profile and viability?
                        * State clearly how the current understanding has evolved from the previous cycle.

                    **2.  Identify Remaining Gaps in Understanding Artisan Digital's Viability:**
                        * Based on your assessment, what is the single most significant unanswered question that a prudent loan officer at EuroFin Bank would have?
                        * Frame this gap as a clear, specific question.

                    **3.  Formulate Next Key Analytical Step:**
                        * Define the single most important *analytical task* for the next cycle that will directly address the key question you just identified.

                    **4.  Propose a Directive:**
                        * Draft a clear, high-level plan for the next directive you will issue to your team. This directive must be based on the verified data schemas from Step 0.
                    """
                )                
                reasoning_response = self.senior_agent.invoke([senior_reasoning_prompt, senior_input_message])
                reasoning_text = str(reasoning_response.content)
                
                yield {"type": "reasoning", "author": "Senior Analyst", "content": reasoning_text}

                senior_directive_prompt = SystemMessage(content="Based on the reasoning, extract the final directive.")
                directive_response = self.senior_agent.invoke([senior_directive_prompt, HumanMessage(content=reasoning_text)])
                next_directive_for_statistician = str(directive_response.content)
                
                yield {"type": "directive", "author": "Senior Analyst", "content": next_directive_for_statistician}

        yield {"type": "system", "author": "System", "content": "📝 Synthesizing Final Business Report..."}
        self.run_final_summary(all_generated_plots)
        yield {"type": "attachment", "author": "System", "content": "Generated final report: `final_business_report.md`", "path": "output/final_business_report.md"}
    
    def run_final_summary(self, all_plot_paths: list):
        """A non-yielding version of the final summary for simplicity in the app."""
        print("\n--- 📝 Synthesizing Final Business Report ---")
        report_files = glob.glob("output/intermediate_report_*.md")
        if not report_files:
            print("⚠️ No intermediate reports found to summarize.")
            return

        all_reports_content = []
        for report_file in sorted(report_files):
            with open(report_file, "r", encoding="utf-8") as f:
                content = f.read()
                all_reports_content.append(f"--- START OF REPORT: {os.path.basename(report_file)} ---\n\n{content}\n\n--- END OF REPORT ---\n\n")

        final_summary_prompt = SystemMessage(
            content="""You are the Finalizer AI for the **Render B2B Credit Assessment Platform**... [Your full Finalizer prompt here]"""
        )
        
        plot_list_markdown = "\n".join([f"- `{path}`" for path in all_plot_paths])
        final_context = (
            f"Here are the intermediate reports for my review:\n\n{''.join(all_reports_content)}\n\n"
            f"Here is the complete list of available plot filenames for embedding in my report:\n{plot_list_markdown}"
        )

        final_summary = self.finalizer_agent.invoke([final_summary_prompt, HumanMessage(content=final_context)]).content
        final_report_tools = FileManagementToolkit(root_dir="./output", selected_tools=["write_file"]).get_tools()
        final_report_tools[0].invoke({"file_path": "final_business_report.md", "text": final_summary})
        
        print("✅ Final business report saved to output/final_business_report.md")