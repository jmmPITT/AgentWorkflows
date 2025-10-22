from crewai import Crew, Process
from agents import get_agents
from tasks import get_tasks
from crewai.llm import LLM

def assemble_crew(llm_instance: LLM, paper_text: str = "", figure_paths: str = ""):
    """Assembles and returns the scientific review crew with parallel execution."""
    agents = get_agents(llm_instance)
    tasks = get_tasks(agents, paper_text, figure_paths)
    
    return Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,  # Sequential with async tasks for parallel execution
        verbose=True
    )