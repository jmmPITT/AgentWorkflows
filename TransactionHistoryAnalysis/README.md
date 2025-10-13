# Transaction History Analysis

This project analyzes transaction history data to identify spending patterns and generate a financial report.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/your-repository.git
    ```
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Navigate to the `TransactionHistoryAnalysis` directory:
    ```bash
    cd TransactionHistoryAnalysis
    ```
2.  Configure your credentials in `src/config.py`:
    ```python
    # config.py
    PROJECT_ID = "your-google-cloud-project-id"
    MODEL_NAME = "gemini-2.5-flash"
    MAX_TURNS = 10
    ```
3.  Run the application:
    ```bash
    python -m src.multi_agent_main
    ```

This will generate a `final_business_report.md` file in the `output` directory.
