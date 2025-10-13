# agents.py

import os
import glob
import base64
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage, HumanMessage
from langchain_google_vertexai import ChatVertexAI
from langchain_experimental.tools import PythonREPLTool
from langchain_community.agent_toolkits import FileManagementToolkit

from agent_tools import get_analyst_tools, get_statistician_tools
from graph_builder import create_agent_workflow
import config

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

class AgentOrchestrator:
    def __init__(self):
        """Initializes the LLM and builds all agent workflows."""
        self.llm = ChatVertexAI(project=config.PROJECT_ID, model=config.MODEL_NAME)
        
        # Senior is a pure LLM for directing.
        self.senior_agent = self.llm
        
        # The Statistician has two roles, requiring two agent instances.
        # 1. The PLANNER: A pure LLM for turn-by-turn directives.
        self.statistician_planner_agent = self.llm
        # 2. The REPORTER: A tool-using agent to write the final report.
        statistician_reporter_tools = get_statistician_tools()
        self.statistician_reporter_agent = create_agent_workflow(self.llm, statistician_reporter_tools)
        
        # The Finalizer is a pure LLM for the last step.
        self.finalizer_agent = self.llm
        
        # Analyst remains a tool-using graph.
        self.persistent_repl = PythonREPLTool()
        analyst_tools = get_analyst_tools(self.persistent_repl)
        self.analyst_agent = create_agent_workflow(self.llm, analyst_tools, internal_turn_limit=3)
        
        print("✅ Corrected 4-Agent Orchestrator Initialized.")

    def run_statistician_analyst_loop(self, high_level_directive: str, cycle_num: int):
        print(f"\n--- 🔬 Kicking off Statistician & Analyst Sub-Workflow (Cycle {cycle_num}) ---")
        
        conversation_history = []
        structured_log = [] # This is the correct variable we should be using
        
        for i in range(5):
            print(f"\n--- 🔄 Inner Cycle {i + 1}/5 ---")

            try:
                directory_listing = os.listdir("output")
            except FileNotFoundError:
                directory_listing = []
            
            history_so_far = ""
            for msg in conversation_history:
                if isinstance(msg, AIMessage):
                    history_so_far += f"\n**Your Last Turn (Thought & Directive):**\n{msg.content}"
                elif isinstance(msg, HumanMessage):
                    if isinstance(msg.content, list):
                        for part in msg.content:
                            if part.get("type") == "text":
                                history_so_far += f"\n**Analyst's Last Output:**\n{part['text']}"
                    else:
                         history_so_far += f"\n**Analyst's Last Output:**\n{msg.content}"

            full_context = (
                f"**High-Level Directive for this Cycle:**\n{high_level_directive}\n\n"
                f"**Current Contents of `/output` Directory:**\n{directory_listing}\n\n"
                f"**Session History So Far:**\n{history_so_far}"
            )

            print("🧠 Statistician (Planner) is reasoning...")
            statistician_system_prompt = SystemMessage(
                content="""You are a meticulous Statistician planning an EDA.

                **CONTEXT REVIEW:**
                - You have been provided with a **High-Level Directive**, the **current contents of the `/output` directory**, and the full **Session History**.
                - Review this complete context to understand what has been done and what to do next.
                - The analyst's Python environment is STATEFUL. Variables persist. Do not reload data unless necessary.
                - The dataframe `df` columns are `['transaction_id', 'timestamp', 'description', 'amount', 'currency', 'balance', 'merchant_name', 'category']`. Pay close attention to case sensitivity.

                **INSTRUCTIONS:**
                1. Based on the full context, write a step-by-step **Thought** process for your next action.
                2. Then, provide a single, specific Python **Directive**.
                3. If the Analyst returned an error in the last turn, your primary goal is to correct it.
                """
            )
            
            messages_for_planner = [statistician_system_prompt, HumanMessage(content=full_context)]
            if conversation_history and isinstance(conversation_history[-1], HumanMessage) and isinstance(conversation_history[-1].content, list):
                messages_for_planner.append(conversation_history[-1])

            statistician_response = self.statistician_planner_agent.invoke(messages_for_planner)
            statistician_response_text = statistician_response.content
            
            try:
                thought = statistician_response_text.split("**Directive:**")[0].replace("**Thought:**", "").strip()
                directive = statistician_response_text.split("**Directive:**")[1].strip().strip('```python').strip('```').strip()
            except IndexError:
                thought = "No thought process articulated."
                directive = statistician_response_text.strip()

            print(f"🤔 Statistician's Thought: {thought}")
            print(f"📄 Statistician's Directive:\n```python\n{directive}\n```")
            conversation_history.append(AIMessage(content=statistician_response_text))

            if "finish" in thought.lower() and i > 1:
                 print("🏁 Statistician has decided to end this analysis cycle.")
                 break

            print("🛠️ Analyst is executing the directive...")
            analyst_system_prompt = (
                "You are a data analyst who executes Python commands. "
                "When a script creates a plot, you **MUST** save it to the `output/` directory and print a confirmation: "
                "'Plot saved successfully to output/filename.png'."
                "Always begin plotting scripts with: `import matplotlib; matplotlib.use('Agg')`."
            )
            
            analyst_inputs = {"messages": [("system", analyst_system_prompt), ("user", directive)], "turn_counter": 0}

            analyst_tool_output = ""
            generated_plots = []
            for event in self.analyst_agent.stream(analyst_inputs):
                for node_name, value in event.items():
                    messages = value.get("messages", [])
                    for message in messages:
                        if isinstance(message, ToolMessage):
                            analyst_tool_output += message.content + "\n"
                            if "Plot saved successfully to" in message.content:
                                for line in message.content.split('\n'):
                                    if "Plot saved successfully to" in line:
                                        path = line.split("output/")[-1].strip().replace("'", "").replace('"', '')
                                        generated_plots.append(f"output/{path}")
            
            # ** THE FIX IS HERE **
            # This line now correctly appends a dictionary to our 'structured_log'.
            structured_log.append({
                "directive": directive,
                "result": analyst_tool_output,
                "plots": generated_plots
            })
            
            analyst_summary_for_stat = f"I have completed the task. Here is the raw output:\n{analyst_tool_output}"
            
            if generated_plots:
                print(f"🖼️  Analyst produced {len(generated_plots)} plot(s). Encoding for Statistician's review.")
                human_message_content = [{"type": "text", "text": analyst_summary_for_stat}]
                for plot_path in generated_plots:
                    if os.path.exists(plot_path):
                        base64_image = encode_image(plot_path)
                        human_message_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}})
                conversation_history.append(HumanMessage(content=human_message_content))
            else:
                conversation_history.append(HumanMessage(content=analyst_summary_for_stat))
        
        print("\n--- ✍️  Statistician (Reporter) is writing intermediate report... ---")
        
        log_as_string = ""
        for i, entry in enumerate(structured_log):
            log_as_string += f"### Turn {i+1}\n\n**Directive:**\n```python\n{entry['directive']}\n```\n\n**Result:**\n```text\n{entry['result']}\n```\n"
            if entry['plots']:
                log_as_string += "**Plots Generated:**\n" + "\n".join([f"- `{path}`" for path in entry['plots']]) + "\n\n"

        summary_prompt = (
            "You are a statistician writing an intermediate report. Synthesize the provided structured logs into a well-organized markdown report. "
            "When referencing a plot, you MUST embed it using the correct relative path, for example: `![Caption](/output/figure.png)`."
        )
        
        summary_input = (
            f"Please create an intermediate analysis report based on the following logs.\n\n"
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
            return report_content
        except FileNotFoundError:
            print(f"⚠️ Statistician failed to write the report file.")
            return "Error: The statistician failed to produce a report."

    def run_final_summary(self):
        """Gathers all reports and has the Finalizer create the definitive business summary."""
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
            content=(
                "You are a senior executive editor. You have been given a series of intermediate analysis reports. "
                "Your task is to synthesize all of them into a single, cohesive, and actionable business deliverable. "
                "Focus on the key insights, ignore redundant steps, and present a final, polished report in markdown format."
            )
        )
        
        final_summary = self.finalizer_agent.invoke(
            [final_summary_prompt, HumanMessage(content="".join(all_reports_content))]
        ).content

        final_report_tools = FileManagementToolkit(
            root_dir="./output",
            selected_tools=["write_file"]
        ).get_tools()
        write_file_tool = final_report_tools[0]
        write_file_tool.invoke({"file_path": "final_business_report.md", "text": final_summary})
        
        print("✅ Final business report saved to output/final_business_report.md")

    def run(self, local_csv_path: str):
        print("--- 🎬 Kicking off the Main Workflow ---")
        safe_local_path = local_csv_path.replace("\\", "/")
        
        next_directive_for_statistician = f"Please begin a thorough exploratory data analysis of the dataset at '{safe_local_path}'."

        for i in range(1, 6):
            print(f"\n--- 👑 Outer Cycle {i}/5 ---")
            
            report_from_statistician = self.run_statistician_analyst_loop(next_directive_for_statistician, i)
            
            if i < 5: # Don't ask for a new directive after the last cycle
                print("\n🧠 Senior is reviewing the intermediate report and plots...")

                # ** THE FIX IS HERE **
                # 1. Gather all figures generated in the last cycle.
                all_figure_paths = glob.glob("output/*.png")

                # 2. Build a multi-modal message with the report text and all images.
                human_message_content = [{"type": "text", "text": report_from_statistician}]
                all_figure_paths = glob.glob("output/*.png")
                if all_figure_paths:
                    print(f"🖼️  Encoding {len(all_figure_paths)} plot(s) for Senior's review.")
                    for plot_path in all_figure_paths:
                        if os.path.exists(plot_path):
                            base64_image = encode_image(plot_path)
                            human_message_content.append(
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                            )
                
                senior_system_prompt = SystemMessage(
                    content="""You are the Senior Director AI, the orchestrator of a multi-agent financial analysis team.

                        ## Core Objective
                        Your ultimate purpose is not just to manage a workflow, but to deeply understand the applicant's financial health to provide robust **decision support for a human**. Your goal is to uncover the ground truth of the applicant's viability, moving beyond surface-level statistics to build a comprehensive, evidence-based narrative. Every directive you issue must be aimed at reducing uncertainty and getting closer to a confident final recommendation.

                        ## Operational Workflow & Team
                        You operate within a strict **five-cycle analytical loop**. Your team consists of a **Statistician AI** (who directs an Analyst AI) and a **Finalizer AI** that will synthesize your team's work after the fifth cycle. In each cycle, you will review the Statistician's markdown report and all associated plots to issue the next directive.

                        ## Mandatory Reasoning Protocol & Output Format
                        You MUST structure your entire response according to the following four-step reasoning protocol. Only the text following the "Final Directive" heading will be sent to the next agent.

                        **1. Synthesize Key Findings:**
                        [Summarize the most critical insights from the latest report and visuals.]

                        **2. Identify Knowledge Gaps:**
                        [Based on the synthesis, identify the most significant unknown or uncertainty.]

                        **3. Formulate Next Key Question:**
                        [State the single, most important analytical question to answer in the next cycle.]

                        **4. Final Directive:**
                        [Based ONLY on the key question, formulate a precise and actionable directive for the Statistician. You MUST frequently request specific data visualizations.]
                        """
                )

                senior_input_message = HumanMessage(content=human_message_content)
                
                # Invoke the Senior agent
                senior_response = self.senior_agent.invoke(
                    [senior_system_prompt, senior_input_message]
                )
                full_response_text = senior_response.content

                # ** THE FIX IS HERE **
                # 1. Print the full chain of thought for visibility.
                print("--- Senior's Full Reasoning ---")
                print(full_response_text)
                print("-----------------------------")

                # 2. Parse the response to extract only the final directive.
                try:
                    # We split the response by our specified heading
                    directive_part = full_response_text.split("4. Final Directive:")[1].strip()
                    next_directive_for_statistician = directive_part
                except IndexError:
                    # Fallback in case the model doesn't follow the format perfectly
                    print("⚠️ Senior did not use the specified format. Using full response as directive.")
                    next_directive_for_statistician = full_response_text
                
                print(f"✅ Senior's Next Directive: {next_directive_for_statistician}")

        self.run_final_summary()
        
        print("\n--- ✅ Entire Workflow Complete. ---")