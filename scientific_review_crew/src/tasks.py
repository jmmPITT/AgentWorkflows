from crewai import Task, Agent
from pydantic import BaseModel, Field
from typing import Literal, List


# pydantic model for the final, structured output
class PublicationDecision(BaseModel):
    decision: Literal["publish", "reject"] = Field(description="The final binary decision on publication.")
    justification: str = Field(description="A concise, one-paragraph justification for the decision based on the synthesized report.")


def create_analysis_task(agent_instance: Agent, domain: str, paper_text: str = "", figure_paths: str = "") -> Task:
    """ Create a standardized multimodal analysis task for a specialist agent """
    return Task(
        description=(
            f"As an elite {domain} scientific reviewer, conduct an uncompromising, rigorous analysis of the provided research paper. You are part of a movement to restore scientific publishing to its noble purpose. Evaluate this paper based on the highest standards of scientific integrity: methodological rigor, reproducibility, genuine novelty, logical consistency, and intellectual honesty.\n\n"
            f"--- RESEARCH PAPER TEXT ---\n{paper_text}\n--- END OF TEXT ---\n\n"
            f"--- ASSOCIATED FIGURES ---\nFigure paths: {figure_paths}\n--- END OF FIGURES ---\n\n"
            "CRITICAL EVALUATION CRITERIA:\n"
            "• Methodological rigor and experimental design\n"
            "• Statistical soundness and reproducibility\n"
            "• Genuine novelty vs. superficial innovation\n"
            "• Logical consistency and theoretical grounding\n"
            "• Appropriate scope and realistic claims\n"
            "• Ethical considerations and conflicts of interest\n"
            "• Evidence of p-hacking, selective reporting, or data manipulation\n\n"
            "Reject the current paradigm of publishing for clicks, citations, or commercial interests. Your mission is to uphold the highest standards of scientific integrity. Use your web search tool to verify at least three key claims and check for reproducibility concerns."
        ),
        expected_output=(
            "Write your response in proper markdown format with the following five sections:\n\n"
            "## Summary\n"
            "[Provide an uncompromising scientific assessment of the paper's core claims, methodology, and conclusions. Focus on scientific rigor, reproducibility, and intellectual honesty]\n\n"
            "## Scientific Strengths\n"
            "- [Bullet point 1 - focus on methodological rigor, reproducibility, genuine novelty]\n"
            "- [Bullet point 2 - focus on statistical soundness, logical consistency]\n"
            "- [Continue with more strengths that demonstrate scientific integrity]\n\n"
            "## Critical Weaknesses & Scientific Concerns\n"
            "- [Bullet point 1 - methodological flaws, reproducibility issues]\n"
            "- [Bullet point 2 - statistical problems, logical inconsistencies]\n"
            "- [Continue with more weaknesses that compromise scientific integrity]\n\n"
            "## Figure Analysis\n"
            "For each figure, provide:\n"
            "- **Figure X:** [Description of what it purports to show]\n"
            "- **Scientific Evaluation:** [Assessment of methodological soundness, statistical validity, and reproducibility]\n\n"
            "## Verified Claims & Reproducibility Assessment\n"
            "For each claim you verified:\n"
            "- **Claim:** [The specific claim]\n"
            "- **Verification:** [How you verified it and assessment of reproducibility]\n"
            "- **Citation:** [Source and link]\n\n"
            "IMPORTANT: Write in actual markdown format, not JSON or any other structured format. Focus on scientific integrity, not commercial appeal."
        ),
        agent=agent_instance,
        async_execution=True  # Enable parallel execution for specialist tasks
    )

def get_tasks(agents: dict, paper_text: str = "", figure_paths: str = "") -> List[Task]:
    """ Create a list of all tasks for the crew with proper dependencies for parallel execution"""

    specialist_agents = {k: v for k, v in agents.items() if k not in ['compiler', 'editor']}
    analysis_tasks = [create_analysis_task(agent, domain, paper_text, figure_paths) for domain, agent in specialist_agents.items()]

    synthesis_task = Task(
        description="Synthesize the independent elite specialist reviews into one comprehensive, uncompromising scientific assessment. You are part of the movement to restore scientific publishing to its noble purpose. Your synthesis must maintain the highest standards of scientific integrity, highlighting both genuine contributions and critical flaws identified by the specialist reviewers. Do not sugar-coat serious scientific concerns or downplay methodological flaws.",
        expected_output="A well-organized markdown document with a main summary focused on scientific integrity, followed by sections for each specialist's analysis (including their figure analysis). Emphasize reproducibility, methodological rigor, and intellectual honesty throughout.",
        agent=agents['compiler'],
        context=analysis_tasks  # This creates dependency on all analysis tasks
    )
    
    editorial_task = Task(
        description="As the final guardian of scientific quality, review the comprehensive assessment and make a definitive publication decision based on uncompromising scientific standards. Prioritize scientific integrity, methodological rigor, reproducibility, and genuine intellectual contribution over commercial appeal, citation potential, or trendy topics. You are part of the movement to restore scientific publishing to its noble purpose.",
        expected_output="A comprehensive markdown report with: 1) Clear decision at the top (PUBLISH or REJECT), 2) Detailed justification of at least 500 words explaining the decision based on scientific integrity criteria: methodological rigor, reproducibility, statistical soundness, genuine novelty, logical consistency, and intellectual honesty. Address any concerns about p-hacking, selective reporting, or research designed for commercial appeal rather than scientific advancement.",
        agent=agents['editor'],
        context=[synthesis_task]  # This creates dependency on synthesis task
    )

    return [*analysis_tasks, synthesis_task, editorial_task]