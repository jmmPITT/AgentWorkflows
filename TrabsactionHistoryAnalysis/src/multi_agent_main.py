# multi_agent_main.py

# ** THE FIX IS HERE **
# Set the backend for the entire script before any other imports that might use it.
import matplotlib
matplotlib.use('Agg')

import os
from agents import AgentOrchestrator

# Get the absolute path to the project root directory (TrabsactionHistoryAnalysis)
# This is two levels up from the current file (src/multi_agent_main.py)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Change the current working directory to the project root
os.chdir(PROJECT_ROOT)

def main():
    """
    The main entry point for the multi-agent system.
    """
    # Ensure the output directory exists
    if not os.path.exists("output"):
        os.makedirs("output")
        
    local_csv_path = "data/artisan_digital_transactions.csv"
    
    orchestrator = AgentOrchestrator()
    
    # MODIFIED: A single call to the new main run method
    orchestrator.run(local_csv_path)

if __name__ == "__main__":
    main()