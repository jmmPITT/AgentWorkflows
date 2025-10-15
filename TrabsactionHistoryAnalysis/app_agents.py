# app_agents.py

import os
import glob
import re
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage, HumanMessage
from langchain_google_vertexai import ChatVertexAI
from langchain_experimental.tools import PythonREPLTool
from langchain_community.agent_toolkits import FileManagementToolkit

from agent_tools import get_statistician_tools
from graph_builder import create_agent_workflow
from rag_agent import RAGAgent
import config

def summarize_tool_output(output: str, max_length: int = 1500) -> str:
    """Truncates the output of a tool to prevent prompt poisoning."""
    if len(output) > max_length:
        truncated_output = output[:max_length]
        last_newline = truncated_output.rfind('\n')
        if last_newline != -1:
            truncated_output = truncated_output[:last_newline]
        return truncated_output + "\n\n... [Output truncated for brevity] ..."
    return output

class AppAgentOrchestrator:
    """Orchestrates the multi-agent workflow for the Streamlit app."""
    def __init__(self):
        # General purpose model for reasoning and planning agents
        self.llm = ChatVertexAI(project=config.PROJECT_ID, model_name=config.MODEL_NAME)
        self.senior_agent = self.llm
        self.statistician_agent = self.llm
        self.finalizer_agent = self.llm
        
        # *** NEW: Specialized model for the coding agent ***
        self.software_engineer_agent = ChatVertexAI(
            project=config.PROJECT_ID,
            model_name="codestral-2501", # From the Model ID in your screenshot
            publisher="mistralai"       # From the Model ID in your screenshot
        )
        # ******************************************************
        
        try:
            self.rag_agent = RAGAgent()
        except FileNotFoundError as e:
            print(f"CRITICAL ERROR: {e}")
            raise
        statistician_reporter_tools = get_statistician_tools()
        self.statistician_reporter_agent = create_agent_workflow(self.llm, statistician_reporter_tools)

    def run_engineer_analyst_loop(self, statistician_directive: str):
        """
        Runs the new inner loop between the Software Engineer and the Analyst.
        The SE writes code, the Analyst executes it. If it fails, the SE tries to fix it.
        This loop runs for a maximum of 5 attempts.
        """
        yield {"type": "system", "author": "System", "content": "🎬 Kicking off Engineer & Analyst Sub-Workflow..."}

        # State management for this inner loop is self-contained.
        engineer_conversation_history = []
        code_to_execute = ""
        final_output = ""
        files_before = set(os.listdir("output")) if os.path.exists("output") else set()

        engineer_system_prompt = SystemMessage(
            content="""You are a senior Python Software Engineer. Your sole purpose is to convert a natural language directive from a Bayesian Data Scientist into a single, executable Python script.

            ## Critical Instructions
            1.  **Output Format:** You MUST ONLY output a single Python code block. Do not add any conversational text, reasoning, or explanations before or after the code block.
            2.  **File Paths:** All file paths MUST be relative and start with `output/`. NEVER use a leading slash.
            3.  **Plotting:** Any script that generates a plot MUST begin with the `matplotlib.use('Agg')` code block to prevent GUI errors in the backend.
            4.  **Output Handling:** The script should NOT print large DataFrames. It should perform its task and print a single, simple confirmation message upon successful completion.
            5.  **Error Correction:** If you are shown a script and a traceback, your task is to identify the error, correct the script, and provide the complete, corrected code block as your response.
            """
        )

        initial_prompt = HumanMessage(content=f"Please write the Python code to accomplish the following task:\n\n{statistician_directive}")
        engineer_conversation_history.append(initial_prompt)

        for attempt in range(5): # This loop runs for 5 iterations as requested
            yield {"type": "system", "author": "System", "content": f"⚙️ Engineer-Analyst Attempt {attempt + 1}/5"}

            # 1. Engineer writes or corrects the code
            yield {"type": "system", "author": "System", "content": "🧠 Software Engineer is writing the code..."}
            # This call now uses the specialized DeepSeek Coder model
            engineer_response = self.software_engineer_agent.invoke([engineer_system_prompt] + engineer_conversation_history)
            engineer_response_text = str(engineer_response.content)

            code_match = re.search(r"```python\n(.*?)```", engineer_response_text, re.DOTALL)
            if code_match:
                code_to_execute = code_match.group(1).strip()
                yield {"type": "directive", "author": "Software Engineer", "content": code_to_execute}
            else:
                error_message = "CRITICAL ERROR: Software Engineer failed to produce a valid Python code block."
                yield {"type": "system", "author": "System", "content": f"⚠️ {error_message}"}
                final_output = error_message
                break

            # 2. Analyst executes the code
            yield {"type": "system", "author": "System", "content": f"🛠️ Analyst is executing the code..."}
            try:
                stateless_repl = PythonREPLTool()
                analyst_tool_output = stateless_repl.invoke(code_to_execute)

                if "Traceback" in analyst_tool_output or "Error" in analyst_tool_output:
                     raise Exception(analyst_tool_output)

                # Success case
                yield {"type": "system", "author": "System", "content": f"✅ Execution successful on attempt {attempt + 1}."}
                yield {"type": "analyst_output", "author": "Analyst", "content": analyst_tool_output}
                final_output = analyst_tool_output
                break

            except Exception as e:
                # Failure case
                error_message = str(e)
                yield {"type": "system", "author": "System", "content": f"⚠️ Attempt {attempt + 1} failed."}
                yield {"type": "analyst_output", "author": "Analyst", "content": error_message}

                if attempt == 4:
                    final_output = f"Final Error after 5 attempts:\n{error_message}"
                    break

                # Prepare for the next iteration (correction) by updating the engineer's state
                correction_prompt = HumanMessage(
                    content=f"The last script failed with this error. Please fix it.\n\nSCRIPT:\n```python\n{code_to_execute}\n```\n\nERROR:\n```\n{error_message}\n```"
                )
                engineer_conversation_history.append(AIMessage(content=engineer_response_text))
                engineer_conversation_history.append(correction_prompt)

        # 3. Finalize and return results from this inner loop
        files_after = set(os.listdir("output")) if os.path.exists("output") else set()
        new_files = files_after - files_before
        plots_generated = [f"output/{fname}" for fname in new_files if fname.endswith(('.png', '.jpg', '.jpeg'))]

        for plot_path in plots_generated:
            yield {"type": "attachment", "author": "Analyst", "content": f"Generated plot: `{os.path.basename(plot_path)}`", "path": plot_path}

        return {
            "directive_code": code_to_execute,
            "result_summary": summarize_tool_output(final_output),
            "full_result": final_output,
            "plots": plots_generated
        }

    def run_statistician_loop(self, high_level_directive: str, cycle_num: int, previous_report_content: str):
        """
        Runs the iterative sub-workflow for the Statistician.
        The Statistician now only provides natural language directives for the engineer.
        """
        yield {"type": "system", "author": "System", "content": f"🔬 Kicking off Statistician Sub-Workflow (Cycle {cycle_num})"}

        # State management for this middle loop
        statistician_conversation_history = []
        structured_log = []

        # RAG context retrieval is unchanged
        yield {"type": "system", "author": "System", "content": f"📚 Consulting Bayesian textbook with query: '{high_level_directive[:100]}...'"}
        try:
            supplemental_rag_context = self.rag_agent.answer(high_level_directive)
            yield {"type": "reasoning", "author": "System", "content": f"**Retrieved Context:**\n\n{supplemental_rag_context}"}
        except Exception as e:
            error_message = f"Failed to query RAG agent: {e}"
            yield {"type": "system", "author": "System", "content": f"⚠️ {error_message}"}
            supplemental_rag_context = error_message

        for i in range(5): # This loop runs for 5 iterations
            yield {"type": "system", "author": "System", "content": f"🔄 Statistician Cycle {i + 1}/5"}

            try:
                directory_listing = os.listdir("output")
            except FileNotFoundError:
                directory_listing = []

            history_so_far = ""
            for msg in statistician_conversation_history:
                if isinstance(msg, AIMessage):
                    history_so_far += f"\n**Your Last Turn (Reasoning & Directive):**\n{msg.content}"
                elif isinstance(msg, HumanMessage):
                    history_so_far += f"\n**Coding Team's Last Summary:**\n{msg.content}"

            full_context = (
                f"**High-Level Directive for this Cycle:**\n{high_level_directive}\n\n"
                f"**Previous Cycle's Report (for context and schema reference):**\n{previous_report_content}\n\n"
                f"**Current Contents of `output` Directory (Your Long-Term Memory):**\n{directory_listing}\n\n"
                f"**Supplemental Context from Bayesian Analysis Textbook:**\n{supplemental_rag_context}\n\n"
                f"**Session History So Far (This Sub-Workflow):**\n{history_so_far}"
            )

            yield {"type": "system", "author": "System", "content": "🧠 Bayesian Data Scientist is reasoning..."}

            # New Statistician prompt focusing on planning, not coding.
            statistician_system_prompt = SystemMessage(
                content="""You are a meticulous Principal Bayesian Data Scientist. Your purpose is to answer a user's analytical objective by investigating a provided dataset. You will delegate all coding tasks to a skilled Software Engineer.

                ## Core Memory & Grounding
                Your most important source of memory is the 'Previous Cycle's Report'. It contains a `## Data Schema Handover` section that provides the ground truth for all available datasets and their exact column names. You MUST use this to formulate your plan.

                ## YOUR TASK
                Review all the context provided (High-level directive, previous report, file listing, etc.). Based on this, you must formulate your reasoning and then provide the next analytical directive FOR THE SOFTWARE ENGINEER. Your response MUST strictly follow the format below.

                ```markdown
                ## Reasoning
                1.  **Review of Previous Report & Schema:** (Start by acknowledging the data schemas from the last report to ground your plan.)
                2.  **State Your Priors:** (State your belief *before* seeing the results of the new directive.)
                3.  **Gather Evidence (The Directive Plan):** (Describe the goal of the analytical step you want the engineer to perform. Be clear and specific.)
                4.  **Articulate Your Posterior Belief:** (Describe how the evidence you plan to gather will update your beliefs.)

                ## Directive
                (Provide a clear, natural language instruction for the Software Engineer. For example: "Load the 'transactions.csv' file from the 'output' directory. Calculate the total monthly spending and save the result to a new CSV file named 'monthly_spending.csv' in the 'output' directory.")
                ```
                """
            )

            messages_for_statistician = [statistician_system_prompt, HumanMessage(content=full_context)]
            if statistician_conversation_history:
                 messages_for_statistician.extend(statistician_conversation_history)

            statistician_response = self.statistician_agent.invoke(messages_for_statistician)
            statistician_response_text = str(statistician_response.content)
            statistician_conversation_history.append(AIMessage(content=statistician_response_text))

            reasoning, directive_for_engineer = "Could not parse.", ""
            directive_match = re.search(r"##\s*Directive\s*\n(.*?)$", statistician_response_text, re.DOTALL | re.IGNORECASE)
            if directive_match:
                directive_for_engineer = directive_match.group(1).strip()
                reasoning_text = statistician_response_text[:directive_match.start()]
                reasoning = re.sub(r"(?i)##\s*.*Reasoning.*", "", reasoning_text).strip() or "Reasoning section was empty."
            else:
                reasoning = statistician_response_text.strip()

            yield {"type": "reasoning", "author": "Statistician", "content": reasoning}

            if not directive_for_engineer:
                yield {"type": "system", "author": "System", "content": "⚠️ Statistician did not provide a directive. Skipping execution."}
                continue
            
            # Delegate coding and debugging to the new inner loop
            engineer_loop_results = yield from self.run_engineer_analyst_loop(directive_for_engineer)

            structured_log.append({
                "directive": engineer_loop_results["directive_code"],
                "result": engineer_loop_results["full_result"],
                "plots": engineer_loop_results["plots"]
            })
            
            # Update the Statistician's conversation history with the summary from the coding team
            summary_for_stat = f"Task complete. Output summary:\n{engineer_loop_results['result_summary']}"
            statistician_conversation_history.append(HumanMessage(content=summary_for_stat))

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
            "\n1.  **Synthesize Findings:** Interpret the results and explain what the new evidence implies about the overall objective of the analysis."
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
            "\n    * **Correct format:** `![Caption](/output/figure_name.png)` (with a leading slash)"
            "\n    * **Incorrect format:** `![Caption](output/figure_name.png)` (without a leading slash)"
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

    def run(self, local_csv_path: str, user_prompt: str):
        yield {"type": "system", "author": "System", "content": "🎬 Kicking off the Main Workflow..."}
        
        safe_local_path = local_csv_path.replace('\\', '/')
        next_directive_for_statistician = (
            f"The user has uploaded the dataset located at '{safe_local_path}'. "
            f"Their primary analytical objective is: '{user_prompt}'"
        )
        
        all_generated_plots = []
        report_from_previous_cycle = "This is the first cycle. No previous report exists."

        for i in range(1, 6):
            yield {"type": "system", "author": "System", "content": f"👑 Outer Cycle {i}/5"}
            
            # Updated to call the new statistician loop
            report_from_statistician, figures_from_last_cycle = yield from self.run_statistician_loop(
                next_directive_for_statistician, i, report_from_previous_cycle
            )
            
            report_from_previous_cycle = report_from_statistician

            if figures_from_last_cycle:
                all_generated_plots.extend(figures_from_last_cycle)

            if i < 5:
                yield {"type": "system", "author": "System", "content": "🧠 Senior Analyst is reviewing the report..."}
                
                senior_input_message = HumanMessage(content=report_from_statistician)
                senior_reasoning_prompt = SystemMessage(
                    content="""You are a Principal Analyst AI, a master of synthesis and strategic reasoning. Your function is to lead a data analysis by forming a deep understanding of the provided dataset and the user's objective. You are loyal only to empirical evidence and the pursuit of truth within the data.

                    ## Guiding Philosophy: From Data to Decision
                    Your ultimate purpose is to transform raw data into a clear, evidence-based narrative that provides robust **decision support for a human**. You do not just answer questions; you deconstruct them, challenge their assumptions, and ensure the analysis is relentlessly focused on delivering actionable insight.

                    ## The Analytical Framework: An Iterative Process
                    You guide a specialist AI team through a structured, multi-cycle review. Each cycle must logically build upon the last. Your role is to ensure this progression is intelligent and efficient.

                    ## Mandatory Reasoning Protocol
                    At the start of each cycle, you are given the latest report from your team. You MUST analyze this information and then articulate your strategic reasoning by following and writing out these steps in exhaustive detail:

                    **STEP 0: GROUNDING & SCHEMA VERIFICATION (CRITICAL FIRST STEP)**
                    - Before all else, your first action is one of **curiosity and discovery**.
                    - If the report provides a `## Data Schema Handover` section, you MUST locate it. This is your **ground truth**. Explicitly list the datasets and their exact column names in your reasoning.
                    - **If no schema is provided** (e.g., this is the first cycle or the last report failed), your reasoning MUST reflect this knowledge gap. Your primary goal is to **discover the schema**. Your proposed directive in Step 4 must therefore be to instruct your team to perform a basic data inspection (`df.info()`, `df.head()`, `df.describe()`) to establish this factual baseline. **Do not propose any other analysis until the schema is known.**

                    **STEP 1: SYNTHESIZE THE CURRENT STATE OF KNOWLEDGE**
                    - Synthesize the most critical, business-relevant insights from the latest report and any accompanying visuals. What is the single most important, undeniable fact we have learned so far?
                    - State clearly how the current understanding has evolved from the previous cycle.

                    **STEP 2: IDENTIFY THE MOST CRITICAL GAP**
                    - Based on your synthesis and the user's ultimate objective, what is the single most significant unanswered question that prevents a confident decision?
                    - Frame this gap as a clear, specific question. This is not about what is merely interesting, but what is essential.

                    **STEP 3: FORMULATE THE NEXT ANALYTICAL TASK**
                    - Define the single most important *analytical task* for the next cycle that will directly and efficiently answer the key question you just identified.

                    **STEP 4: PROPOSE THE NEXT DIRECTIVE**
                    - Based on the verified data schemas from Step 0 and the analytical task from Step 3, draft a clear, high-level plan for the next directive you will issue to your team.
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
        
        self.run_final_summary(all_generated_plots, user_prompt)
        
        yield {"type": "attachment", "author": "System", "content": "Generated final report: `final_business_report.md`", "path": "output/final_business_report.md"}
    
    def run_final_summary(self, all_plot_paths: list, user_prompt: str):
        """A non-yielding version of the final summary that now accepts the user_prompt."""
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
            content="""You are the Finalizer AI, a specialist in synthesizing complex, multi-cycle data analysis into a clear, professional, and actionable business report.

                ## Core Objective & Audience
                Your ultimate purpose is to provide robust **decision support for the human user who asked the original question**. The iterative analysis is complete. Your task is to transform the series of technical, intermediate reports into a final, polished assessment that directly addresses the user's initial objective.

                ## Your Input Materials
                1.  **User's Objective:** The original question or goal the user provided. Your entire report, especially the Executive Summary, must be framed as a direct answer to this.
                2.  **Intermediate Reports:** The full text of all intermediate reports from your AI team.
                3.  **List of Visualizations:** A definitive list of all available image files.

                ## Mandatory Report Structure
                You MUST structure your final output using the following five sections:

                **1. Executive Summary:**
                Begin with a brief, high-level overview that directly answers the user's original objective. Conclude with a clear recommendation (e.g., Favorable, Unfavorable) and a Confidence Score (High, Medium, Low).

                **2. Key Positive Findings (Strengths):**
                A bulleted list of positive findings supporting a favorable view. Each point MUST be backed by specific evidence from the reports. Embed relevant visualizations here.

                **3. Key Negative Findings (Risks / Weaknesses):**
                A bulleted list of negative findings or areas of concern. Each point MUST be backed by specific evidence. Embed relevant visualizations here.

                **4. Summary of Analytical Journey:**
                Briefly narrate how the analysis progressed, highlighting key discoveries or shifts in strategy that led to the final conclusions.

                **5. Appendix: Complete List of Visualizations:**
                A simple, bulleted list of the filenames of all generated visualizations.

                ## Critical Formatting Instructions
                - **Embed All Relevant Figures:** You MUST embed figures in the 'Key Positive Findings' and 'Key Negative Findings' sections.
                - **Use Correct Markdown Syntax:** The markdown for an image MUST be: `![Descriptive Caption](/output/figure_name.png)`.
                """
        )
        
        plot_list_markdown = "\n".join([f"- `{path}`" for path in all_plot_paths])
        
        final_context = (
            f"The user's original analytical objective was: '{user_prompt}'\n\n"
            f"Here are the intermediate reports for my review:\n\n{''.join(all_reports_content)}\n\n"
            f"Here is the complete list of available plot filenames for embedding in my report:\n{plot_list_markdown}"
        )

        final_summary = self.finalizer_agent.invoke([final_summary_prompt, HumanMessage(content=final_context)]).content
        final_report_tools = FileManagementToolkit(root_dir="./output", selected_tools=["write_file"]).get_tools()
        final_report_tools[0].invoke({"file_path": "final_business_report.md", "text": final_summary})
        
        print("✅ Final business report saved to output/final_business_report.md")