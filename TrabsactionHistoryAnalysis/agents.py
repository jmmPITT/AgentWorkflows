# agents.py

import os
import glob
import base64
import pickle
import re # Import the regular expressions library
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage, HumanMessage
from langchain_google_vertexai import ChatVertexAI
from langchain_experimental.tools import PythonREPLTool
from langchain_community.agent_toolkits import FileManagementToolkit

from agent_tools import get_analyst_tools, get_statistician_tools
from graph_builder import create_agent_workflow
from rag_agent import RAGAgent
import config

def encode_image(image_path):
    """Encodes an image file to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

class AgentOrchestrator:
    def __init__(self):
        """Initializes the LLM and base agent components."""
        self.llm = ChatVertexAI(project=config.PROJECT_ID, model_name=config.MODEL_NAME)
        
        self.senior_agent = self.llm
        self.statistician_planner_agent = self.llm
        self.finalizer_agent = self.llm
        
        self.rag_agent = RAGAgent()
        
        statistician_reporter_tools = get_statistician_tools()
        self.statistician_reporter_agent = create_agent_workflow(self.llm, statistician_reporter_tools)
        
        print("✅ 5-Agent Orchestrator Initialized (Stateless Analyst Workflow with RAG).")

    def run_statistician_analyst_loop(self, high_level_directive: str, cycle_num: int):
        """
        Runs the iterative sub-workflow between the Statistician and the Analyst.
        """
        print(f"\n--- 🔬 Kicking off Statistician & Analyst Sub-Workflow (Cycle {cycle_num}) ---")
        
        conversation_history = []
        structured_log = []
        supplemental_rag_context = "No context retrieved yet. This is the first turn."
        
        for i in range(5):
            print(f"\n--- 🔄 Inner Cycle {i + 1}/5 ---")

            try:
                directory_listing = os.listdir("output")
            except FileNotFoundError:
                directory_listing = []
            
            history_so_far = ""
            for msg in conversation_history:
                if isinstance(msg, AIMessage):
                    history_so_far += f"\n**Your Last Turn (Reasoning & Directive):**\n{msg.content}"
                elif isinstance(msg, HumanMessage):
                    content_text = ""
                    if isinstance(msg.content, list):
                        for part in msg.content:
                            if part.get("type") == "text":
                                content_text += part['text']
                    else:
                         content_text = str(msg.content)
                    history_so_far += f"\n**Analyst's Last Output:**\n{content_text}"

            full_context = (
                f"**High-Level Directive for this Cycle:**\n{high_level_directive}\n\n"
                f"**Current Contents of `output` Directory (Your Long-Term Memory):**\n{directory_listing}\n\n"
                f"**Supplemental Context from Bayesian Analysis Textbook:**\n{supplemental_rag_context}\n\n"
                f"**Session History So Far:**\n{history_so_far}"
            )

            print("🧠 Statistician (Planner) is reasoning...")
            
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

                ## CORE WORKFLOW: EXPLICIT STATE MANAGEMENT
                Your Analyst's Python environment is **STATELESS**. You MUST use the `output` directory as your persistent memory.
                1.  **LOAD STATE:** Load DataFrames or variables from files in `output`.
                2.  **EXECUTE LOGIC:** Perform the next single, logical step of your analysis.
                3.  **SAVE STATE:** Save any results to a new, clearly named file in `output`.

                ## YOUR TASK
                Review the directive, memory, and history. Formulate your **Reasoning** using the Bayesian framework. Then, write a Python **Directive**. Adhere to all critical instructions.
                """
            )
                        
            messages_for_planner = [statistician_system_prompt, HumanMessage(content=full_context)]
            if conversation_history and isinstance(conversation_history[-1], HumanMessage):
                messages_for_planner.append(conversation_history[-1])

            statistician_response = self.statistician_planner_agent.invoke(messages_for_planner)
            response_content = statistician_response.content
            statistician_response_text = str(response_content)

            # Robustly parse the output using regular expressions
            reasoning_match = re.search(r"(?i)(?s)(?:##\s*Reasoning|Reasoning:)(.*?)(?:##\s*Directive|Directive:)", statistician_response_text)
            directive_match = re.search(r"(?i)(?s)(?:##\s*Directive|Directive:)(.*)", statistician_response_text)

            if reasoning_match and directive_match:
                reasoning = reasoning_match.group(1).strip()
                directive = directive_match.group(1).strip().strip('```python').strip('```').strip()
            else:
                # Fallback for unexpected formats
                reasoning = "Could not parse reasoning. Full response attached."
                directive = statistician_response_text

            if "Could not parse" not in reasoning:
                supplemental_rag_context = self.rag_agent.retrieve_context(reasoning)
            else:
                supplemental_rag_context = "No new context was retrieved due to parsing issue."

            print(f"🤔 Statistician's Reasoning: {reasoning}")
            print(f"📄 Statistician's Directive:\n```python\n{directive}\n```")
            conversation_history.append(AIMessage(content=statistician_response_text))

            if "finish" in reasoning.lower() and i > 1:
                 print("🏁 Statistician has decided to end this analysis cycle.")
                 break

            try:
                files_before = set(os.listdir("output"))
            except FileNotFoundError:
                files_before = set()

            print("🛠️ Analyst is executing the directive in a clean, stateless environment...")
            
            stateless_repl = PythonREPLTool()
            analyst_tools = get_analyst_tools(stateless_repl)
            analyst_agent = create_agent_workflow(self.llm, analyst_tools, internal_turn_limit=3)
            analyst_inputs = {"messages": [("system", "You are a data analyst who executes Python commands exactly as instructed."), ("user", directive)], "turn_counter": 0}

            analyst_tool_output = ""
            for event in analyst_agent.stream(analyst_inputs):
                for node_name, value in event.items():
                    messages = value.get("messages", [])
                    for message in messages:
                        if isinstance(message, ToolMessage):
                            analyst_tool_output += message.content + "\n"
            
            try:
                files_after = set(os.listdir("output"))
            except FileNotFoundError:
                files_after = set()

            new_files = files_after - files_before
            generated_plots = [f"output/{fname}" for fname in new_files if fname.endswith(('.png', '.jpg', '.jpeg'))]
            
            structured_log.append({ "directive": directive, "result": analyst_tool_output, "plots": generated_plots })
            
            analyst_summary_for_stat = f"I have completed the task. Here is the raw output:\n{analyst_tool_output}"
            
            human_message_content = [{"type": "text", "text": analyst_summary_for_stat}]
            if generated_plots:
                print(f"🖼️  Analyst produced {len(generated_plots)} plot(s). Encoding for Statistician's review.")
                for plot_path in generated_plots:
                    if os.path.exists(plot_path):
                        base64_image = encode_image(plot_path)
                        human_message_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}})
            
            conversation_history.append(HumanMessage(content=human_message_content))
        
        print("\n--- ✍️  Statistician (Reporter) is writing intermediate report... ---")
        
        all_figures_this_cycle = sorted(list(set(p for entry in structured_log for p in entry['plots'])))

        log_as_string = ""
        for i, entry in enumerate(structured_log):
            log_as_string += f"### Turn {i+1}\n\n**Directive:**\n```python\n{entry['directive']}\n```\n\n**Result:**\n```text\n{entry['result']}\n```\n"
            if entry['plots']:
                log_as_string += "**Plots Generated in this Turn:**\n" + "\n".join([f"- `{path}`" for path in entry['plots']]) + "\n\n"
        
        summary_prompt = (
            "You are the Statistician Reporter AI. Your audience is your AI supervisor, the Senior Director."
            "\n\n## Core Directive: Document and Save"
            "\nYour single most important task is to create a markdown report summarizing the events of the last work cycle and save it using the `write_file` tool. **You MUST ALWAYS generate a report and call the `write_file` tool, even if the analysis was unsuccessful or the logs are empty.**"
            "\n\n## Instructions:"
            "\n1.  **Review the Input:** You will be given a list of available figures and the structured logs from the cycle."
            "\n2.  **Write the Report:**"
            "\n    - If the logs show successful analysis, synthesize the findings into a clear report."
            "\n    - If the logs show errors, a lack of progress, or are empty, your report MUST clearly state the nature of the failure."
            "\n3.  **Embed Figures:** If there are figures in the 'Figures Available' list, you MUST embed them using the path: `![Caption](/output/figure.png)`. Note the correct relative path without a leading slash."
            "\n4.  **Final Action (Mandatory):** Your final action MUST be to call the `write_file` tool to save your report."
        )
        
        figures_list_str = "\n".join([f"- `{path}`" for path in all_figures_this_cycle])
        summary_input = (
            f"Please create an intermediate analysis report based on the following logs and available figures.\n\n"
            f"**Figures Available for this Report:**\n{figures_list_str}\n\n"
            f"**STRUCTURED LOGS:**\n{log_as_string}"
        )

        report_filename = f"intermediate_report_cycle_{cycle_num}.md"
        final_prompt_for_stat = (
            f"{summary_input}\n\n"
            f"Now, write the full markdown report and save it to the file named '{report_filename}' using your `write_file` tool."
        )

        stat_inputs = {"messages": [("system", summary_prompt), ("user", final_prompt_for_stat)]}
        self.statistician_reporter_agent.invoke(stat_inputs)
        
        try:
            with open(f"output/{report_filename}", "r", encoding='utf-8') as f:
                report_content = f.read()
            print(f"✅ Intermediate report saved to output/{report_filename}")
            return report_content, all_figures_this_cycle
        except FileNotFoundError:
            print(f"⚠️ Statistician failed to write the report file.")
            return "Error: The statistician failed to produce a report.", []

    def run_final_summary(self, all_plot_paths: list):
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
            content="""You are the Finalizer AI for the **Render B2B Credit Assessment Platform**. Your task is to synthesize the entire multi-cycle analysis into a single, comprehensive, and professional **multi-page markdown report** for our partner, **'EuroFin Bank'**.

                ## Core Objective
                Your report must provide definitive **decision support for a human loan officer**. It must construct a rich, evidence-based narrative about the applicant's ('Artisan Digital') true financial health, risks, and **"forward-looking potential"** based on their Open Banking data, moving far beyond the limitations of their **"thin" credit file**. The report should be approximately 3-5 pages in length and must be visually supported with embedded figures.

                ## MANDATORY INSTRUCTIONS
                1.  **Embed All Relevant Visuals:** You have been provided with a complete list of all generated plot filenames. You MUST embed these plots directly into the report using markdown syntax (`![Caption](path/to/figure.png)`) wherever they support your analysis. A report without embedded images is a failure.
                2.  **Create a Narrative, Not a List:** Do not simply list facts. Weave the findings from the intermediate reports and the visual evidence from the plots into a cohesive story about the applicant's financial situation.
                3.  **Adhere to the Structure:** You MUST use the following detailed structure. Expand on each section to create a comprehensive, multi-page document.

                ## Mandatory Report Structure for EuroFin Bank

                **1. Executive Summary:**
                * Begin with a high-level overview of the findings on Artisan Digital.
                * Conclude with a clear recommendation: **Approve, Approve with Conditions, or Deny**.
                * Include a **Confidence Score** (High, Medium, or Low) for your recommendation.

                **2. Analysis of Financial Health & Stability:**
                * **Income Analysis:** Discuss the consistency, sources, and trends of their income. Embed and reference plots like "Top 10 Credit Categories by Total Amount (Income)". Is the income source diversified or singular? What does this imply?
                * **Expense Analysis:** Break down the major cost drivers. Discuss fixed vs. variable costs. Use and embed the "Top 10 Debit Categories by Total Amount (Expenditure)" plot to illustrate where the money is going.
                * **Profitability Analysis:** Analyze the monthly profitability. Is the business consistently profitable or does it experience significant swings? Embed and discuss the "Monthly Net Cash Flow Trend for Artisan Digital" chart to showcase this.

                **3. Liquidity and Cash Flow Assessment (Critical Risk Section):**
                * This is the most important section for risk assessment. Analyze the applicant's ability to manage their cash flow.
                * Discuss the account balance history in detail. Were there periods of negative balance? For how long?
                * You MUST embed and extensively reference the **"Artisan Digital's Daily Account Balance History"** chart as the primary evidence for this section. Point out the lowest balance recorded and the duration of any negative periods.
                * Synthesize this with the "Monthly Net Cash Flow Trend" to explain the story of their liquidity challenges.

                **4. Analysis Narrative:**
                * Summarize the analytical journey. Explain how the iterative process (e.g., correcting errors in Cycle 2, refining categories in Cycle 4) was essential for arriving at a trustworthy and nuanced conclusion. Emphasize how this deep analysis provides a more complete picture than initial, surface-level statistics.

                **5. Appendix: Complete List of Visualizations:**
                * Conclude with a complete, bulleted list of all generated visualizations with their filenames, so the loan officer knows all the evidence that is available for review.
                """
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

    def run(self, local_csv_path: str):
        print("--- 🎬 Kicking off the Main Workflow ---")
        safe_local_path = local_csv_path.replace("\\", "/")
        next_directive_for_statistician = f"Begin the credit risk assessment of 'Artisan Digital' for our partner, 'EuroFin Bank'. Start with a high-level exploratory data analysis of the dataset at '{safe_local_path}' to understand its basic structure, content, and quality. Your first step should be to load the data and save it to a parquet checkpoint."

        all_generated_plots = []

        for i in range(1, 6):
            print(f"\n--- 👑 Outer Cycle {i}/5 ---")
            
            report_from_statistician, figures_from_last_cycle = self.run_statistician_analyst_loop(next_directive_for_statistician, i)
            
            if figures_from_last_cycle:
                all_generated_plots.extend(figures_from_last_cycle)

            if i < 5:
                print("\n🧠 Senior is reviewing the intermediate report and plots...")

                human_message_content = [{"type": "text", "text": report_from_statistician}]
                
                if figures_from_last_cycle:
                    print(f"🖼️  Encoding {len(figures_from_last_cycle)} new plot(s) for Senior's review.")
                    for plot_path in figures_from_last_cycle:
                        if os.path.exists(plot_path):
                            base64_image = encode_image(plot_path)
                            human_message_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}})
                
                senior_input_message = HumanMessage(content=human_message_content)

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
                
                print("--- Senior is Reasoning... ---")
                reasoning_response = self.senior_agent.invoke([senior_reasoning_prompt, senior_input_message])
                reasoning_text = reasoning_response.content
                print(reasoning_text)
                print("-----------------------------")

                senior_directive_prompt = SystemMessage(
                    content="""Based on the provided reasoning, extract and formulate the final, clean, and actionable directive to be sent to the Statistician. Output only the directive itself, with no extra text or headings."""
                )

                print("--- Senior is Formulating Final Directive... ---")
                directive_response = self.senior_agent.invoke([senior_directive_prompt, HumanMessage(content=reasoning_text)])
                next_directive_for_statistician = directive_response.content
                
                print(f"✅ Senior's Next Directive: {next_directive_for_statistician}")

        self.run_final_summary(all_generated_plots)
        
        print("\n--- ✅ Entire Workflow Complete. ---")