# Transaction History Analysis

This project is a multi-agent system designed to analyze transaction data using LangChain and Google Vertex AI. It provides a comprehensive analysis of financial data, including transaction patterns, cash flow, and account balance dynamics.

## Project Overview

The system uses a multi-agent approach to simulate a team of financial analysts. Each agent has a specific role, such as data extraction, statistical analysis, and report generation. The agents collaborate to produce a detailed financial report based on the provided transaction data.

## Features

-   **Multi-Agent System:** A collaborative team of AI agents for in-depth financial analysis.
-   **LangChain Integration:** Utilizes LangChain for building and managing the agent workflow.
-   **Google Vertex AI:** Leverages the power of Google's Vertex AI for advanced language models.
-   **Streamlit Interface:** An interactive web interface for uploading data and viewing results.
-   **Automated Reporting:** Generates detailed intermediate and final reports in Markdown format.
-   **Data Visualization:** Creates charts and graphs to visualize financial data.

## Getting Started

### Prerequisites

-   Python 3.8 or higher
-   Google Cloud Platform project with Vertex AI enabled
-   `gcloud` CLI installed and authenticated

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/TrabsactionHistoryAnalysis.git
    cd TrabsactionHistoryAnalysis
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your Google Cloud project:**

    Open `config.py` and set your `PROJECT_ID` and `MODEL_NAME`.

    ```python
    # config.py

    PROJECT_ID = "your-gcp-project-id"
    MODEL_NAME = "gemini-1.5-flash"
    ```

### Usage

1.  **Run the Streamlit application:**

    ```bash
    streamlit run app.py
    ```

2.  **Upload your transaction data:**

    Use the file uploader to upload a CSV file containing your transaction history.

3.  **Define the analytical objective:**

    In the text area, describe what you want to understand about the data.

4.  **Start the analysis:**

    Click the "Start New Analysis" button to begin the multi-agent workflow. The results, including reports and visualizations, will be displayed in the application.

## Project Structure

```
TrabsactionHistoryAnalysis/
├── example_outputs/            # Example reports and visualizations
├── .gitignore                  # Git ignore file
├── agent_tools.py              # Tools for the agents
├── app.py                      # Streamlit application
├── app_agents.py               # Agent definitions and orchestration
├── config.py                   # Configuration file for GCP project
├── create_vector_store.py      # Script for creating a vector store
├── graph_builder.py            # Builds the agent workflow graph
├── rag_agent.py                # RAG agent for contextual information
└── requirements.txt            # Python dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request with any improvements or new features.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
