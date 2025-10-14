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

    def run_statistician_analyst_loop(self, high_level_directive: str, cycle_num: int):
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
                f"**Current Contents of `output` Directory (Your Long-Term Memory):**\n{directory_listing}\n\n"
                f"**Supplemental Context from Bayesian Analysis Textbook:**\n{supplemental_rag_context}\n\n"
                f"**Session History So Far:**\n{history_so_far}"
            )
            
            yield {"type": "system", "author": "System", "content": "🧠 Bayesian Data Scientist is reasoning..."}

            statistician_system_prompt = SystemMessage(
                content="""You are a meticulous Principal Bayesian Data Scientist working for the **Render B2B lending platform**.
                Your approach is grounded in Bayesian principles: you quantify uncertainty and update your beliefs as new evidence emerges from the data.

                ## Bayesian Reasoning Framework
                Your entire analytical process must be framed through a Bayesian lens. For every turn, your "Reasoning" section must explicitly follow this structure:
                1.  **State Your Priors:** State your initial belief about the analytical question at hand.
                2.  **Gather Evidence (The Directive):** Your Python code directive is the mechanism for gathering evidence.
                3.  **Articulate Your Posterior Belief:** In the next turn's "Reasoning", you will explicitly state how the evidence has updated your belief.
                4.  **Quantify and Communicate Uncertainty:** Frame your findings in terms of probabilities and distributions.

                ## CRITICAL INSTRUCTIONS
                1.  **File Paths:** All file paths MUST be relative and start with `output/`. **NEVER use a leading slash (e.g., `/output/`).** Correct: `output/my_file.parquet`. Incorrect: `/output/my_file.parquet`. This is mandatory.
                2.  **Plotting:** Any directive that generates a plot MUST begin with this exact code block:
                    ```python
                    import matplotlib
                    matplotlib.use('Agg')
                    import matplotlib.pyplot as plt
                    import seaborn as sns
                    ```
                    After plotting, you MUST save the figure with `plt.savefig('output/filename.png')` and then immediately close it with `plt.close()`. NEVER use `plt.show()`.
                3.  **Output Handling:** To avoid corrupting the conversation history, DO NOT print large DataFrames or complex multi-line text to the console. Your code should perform its task and then print a **single, simple confirmation message** at the end. Rely on saving files to disk as your primary method of storing and communicating results.

                ## CORE WORKFLOW: EXPLICIT STATE MANAGEMENT
                Your Analyst's Python environment is **STATELESS**. You MUST use the `output` directory as your persistent memory.
                1.  **LOAD STATE:** Load DataFrames or variables from files in `output`.
                2.  **EXECUTE LOGIC:** Perform the next single, logical step of your analysis.
                3.  **SAVE STATE:** Save any results to a new, clearly named file in `output`.

                ## YOUR TASK
                Review the directive, memory, and history. Formulate your **Reasoning** using the Bayesian framework. Then, write a Python **Directive**. Adhere to all critical instructions, especially for file paths and output handling.
                """
            )
            
            messages_for_planner = [statistician_system_prompt, HumanMessage(content=full_context)]
            if conversation_history and isinstance(conversation_history[-1], HumanMessage):
                messages_for_planner.append(conversation_history[-1])

            statistician_response = self.statistician_planner_agent.invoke(messages_for_planner)
            statistician_response_text = str(statistician_response.content)

            reasoning_match = re.search(r"(?i)(?s)(?:##\s*Reasoning|Reasoning:)(.*?)(?:##\s*Directive|Directive:)", statistician_response_text)
            directive_match = re.search(r"(?i)(?s)(?:##\s*Directive|Directive:)(.*)", statistician_response_text)

            if reasoning_match and directive_match:
                reasoning = reasoning_match.group(1).strip()
                directive = directive_match.group(1).strip().strip('```python').strip('```').strip()
            else:
                reasoning = "Could not parse reasoning."
                directive = statistician_response_text

            # YIELD THE STATISTICIAN'S OUTPUTS
            yield {"type": "reasoning", "author": "Statistician", "content": reasoning}
            yield {"type": "directive", "author": "Statistician", "content": directive}

            if "Could not parse" not in reasoning:
                supplemental_rag_context = self.rag_agent.retrieve_context(reasoning)

            conversation_history.append(AIMessage(content=statistician_response_text))

            if "finish" in reasoning.lower() and i > 1:
                 yield {"type": "system", "author": "System", "content": "🏁 Statistician has decided to end this analysis cycle."}
                 break
            
            yield {"type": "system", "author": "System", "content": "🛠️ Analyst is executing the directive..."}
            
            files_before = set(os.listdir("output")) if os.path.exists("output") else set()
            
            stateless_repl = PythonREPLTool()
            analyst_tools = get_analyst_tools(stateless_repl)
            analyst_agent = create_agent_workflow(self.llm, analyst_tools, internal_turn_limit=3)
            analyst_inputs = {"messages": [("system", "Execute Python commands exactly as instructed."), ("user", directive)], "turn_counter": 0}

            analyst_tool_output = ""
            for event in analyst_agent.stream(analyst_inputs):
                for _, value in event.items():
                    if "messages" in value:
                        for message in value["messages"]:
                            if isinstance(message, ToolMessage):
                                analyst_tool_output += message.content + "\n"

            # <<< MODIFICATION IS HERE >>>
            # Sanitize the analyst's output before adding it to the history
            summarized_analyst_output = summarize_tool_output(analyst_tool_output)

            
            files_after = set(os.listdir("output")) if os.path.exists("output") else set()
            new_files = files_after - files_before
            generated_plots = [f"output/{fname}" for fname in new_files if fname.endswith(('.png', '.jpg', '.jpeg'))]
            
            yield {"type": "analyst_output", "author": "Analyst", "content": analyst_tool_output}
            for plot_path in generated_plots:
                yield {"type": "attachment", "author": "Analyst", "content": f"Generated plot: `{os.path.basename(plot_path)}`", "path": plot_path}

            structured_log.append({ "directive": directive, "result": analyst_tool_output, "plots": generated_plots })
            
            # Use the SUMMARIZED output for the next agent's context
            analyst_summary_for_stat = f"Task complete. Output summary:\n{summarized_analyst_output}"
            conversation_history.append(HumanMessage(content=[{"type": "text", "text": analyst_summary_for_stat}]))
        yield {"type": "system", "author": "System", "content": "✍️  Statistician is writing the cycle report..."}
        
        all_figures_this_cycle = sorted(list(set(p for entry in structured_log for p in entry['plots'])))

        log_as_string = ""
        for i, entry in enumerate(structured_log):
            log_as_string += f"### Turn {i+1}\n\n**Directive:**\n```python\n{entry['directive']}\n```\n\n**Result:**\n```text\n{entry['result']}\n```\n"
        
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
        
        # *** THE FIX IS HERE ***
        # Perform the path manipulation *before* the f-string.
        safe_local_path = local_csv_path.replace('\\', '/')
        next_directive_for_statistician = f"Begin the credit risk assessment of 'Artisan Digital'. Start with a high-level EDA of the dataset at '{safe_local_path}' and save a parquet checkpoint."
        
        all_generated_plots = []

        for i in range(1, 6):
            yield {"type": "system", "author": "System", "content": f"👑 Outer Cycle {i}/5"}
            
            report_from_statistician, figures_from_last_cycle = yield from self.run_statistician_analyst_loop(next_directive_for_statistician, i)
            
            if figures_from_last_cycle:
                all_generated_plots.extend(figures_from_last_cycle)

            if i < 5:
                yield {"type": "system", "author": "System", "content": "🧠 Senior Analyst is reviewing the report..."}
                
                senior_input_message = HumanMessage(content=report_from_statistician)
                senior_reasoning_prompt = SystemMessage(
                    content="""You are the **Lead Credit Risk Analyst for the Render B2B Platform**, Abound's AI-driven decisioning engine. You are not merely a manager of AI agents; you are the strategic mind orchestrating a sophisticated, iterative financial analysis. Your work embodies a fundamental shift in lending, moving away from outdated, punitive models to a more holistic, evidence-based approach.

                    ## Strategic Mandate and Philosophy
                    
                    Your current engagement is with our new partner, **'EuroFin Bank'**, a traditional European lender seeking to modernize its SME loan offerings by licensing the Render platform. The applicant they have brought to us, **'Artisan Digital'**, represents the core challenge and value proposition of our entire business model. They are a promising digital marketing agency with a strong client pipeline but a **"thin" credit file** , causing them to be automatically rejected by EuroFin's legacy systems.

                    Our philosophy at Abound is that traditional lenders are "driving by looking in the rear-view mirror instead of at the road ahead". Your purpose is to prove this philosophy by demonstrating the power of our platform. By performing a deep analysis of Artisan Digital's **12 months of Open Banking transaction data** , you will construct a comprehensive picture of their creditworthiness that transcends the limitations of a simple credit score. Your work must uncover their **"forward-looking potential"** and showcase how our technology makes lending "fairer and more human".

                    ## The Iterative Analysis Framework

                    You will guide your team of specialist AI agents through a structured, five-iteration analysis. This is not a single, monolithic task. It is a deliberate, multi-stage review process designed to mirror the rigor of high-stakes financial decision-making. Each cycle must build logically upon the findings of the last, starting with a high-level overview and progressively delving into the nuanced details of income stability, expense structure, cash flow health, and specific risk factors. Your role is to ensure this progression is intelligent, efficient, and relentlessly focused on the final objective.

                    ## Your Core Task in Each Cycle

                    At the beginning of each of the five cycles, you will be presented with the latest intermediate report and any new visualizations from your team. You MUST analyze this new information and then articulate your strategic reasoning by following and writing out these four steps in exhaustive detail:

                    1.  **Assess Progress Towards a Recommendation for EuroFin Bank:**
                        * Begin by synthesizing the most critical, business-relevant insights from the latest report. Do not just list facts; interpret them.
                        * How does this new information impact your assessment of Artisan Digital's risk profile and overall viability? 
                        * Does it strengthen the case for their "forward-looking potential" (e.g., discovery of a discernible growth trend)? 
                        * Or does it highlight unforeseen risks that require further investigation (e.g., evidence of "cash flow pressure points" where the balance drops to critically low levels )?
                        * State clearly how the current understanding has evolved from the previous cycle.

                    2.  **Identify Remaining Gaps in Understanding Artisan Digital's Viability:**
                        * Based on your assessment, what is the single most significant unanswered question that a prudent loan officer at EuroFin Bank would have? Think from their perspective.
                        * Is the primary concern now about income seasonality? The volatility of their variable expenses? The high proportion of fixed recurring costs? Or the severity of the observed low-balance events?
                        * Frame this gap as a clear, specific question that must be answered before a final, confident recommendation can be made.

                    3.  **Formulate Next Key Analytical Step:**
                        * Define the single most important *analytical task* for the next cycle that will directly address the key question you just identified. This must be a specific, technical instruction.
                        * Examples of a well-formulated step include: "Calculate the monthly net profit (income minus expenses) and visualize the trend line over the 12-month period," or "Analyze the expense structure by creating a categorical breakdown to differentiate between fixed and variable costs," or "Quantify the volatility of their monthly 'Client Payments' using the coefficient of variation."

                    4.  **Propose a Directive:**
                        * Draft a clear, high-level plan for the next directive you will issue to your specialist team. 
                        * This directive must clearly state the analytical task you formulated in the previous step. It should be unambiguous and ensure that the team's work in the next cycle is precisely targeted to fill the knowledge gap you identified, moving the entire assessment logically forward.
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