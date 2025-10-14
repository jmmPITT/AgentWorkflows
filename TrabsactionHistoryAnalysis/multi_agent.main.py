# multi_agent_main.py

# Set the backend for the entire script before any other imports that might use it.
import matplotlib
matplotlib.use('Agg')

import os
from agents import AgentOrchestrator

def main():
    """
    The main entry point for the multi-agent system.
    """
    # Ensure the output directory exists
    if not os.path.exists("output"):
        os.makedirs("output")
        
    local_csv_path = "data/artisan_digital_transactions.csv"
    
    orchestrator = AgentOrchestrator()
    
    orchestrator.run(local_csv_path)

if __name__ == "__main__":
    main()