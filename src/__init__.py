"""
Elite Scientific Review Crew

A revolutionary AI-powered scientific review system that restores integrity 
to academic publishing through uncompromising standards for scientific rigor, 
reproducibility, and intellectual honesty.
"""

__version__ = "1.0.0"
__author__ = "Elite Scientific Review Crew"
__email__ = "contact@elitescientificreview.com"

from .agents import get_agents, create_specialist_agent
from .tasks import get_tasks, create_analysis_task
from .crew import assemble_crew

__all__ = [
    "get_agents",
    "create_specialist_agent", 
    "get_tasks",
    "create_analysis_task",
    "assemble_crew"
]
