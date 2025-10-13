# agent_tools.py

from langchain_experimental.tools import PythonREPLTool
from langchain_community.agent_toolkits import FileManagementToolkit
from pydantic import BaseModel, Field

# The 'Route' class and 'get_senior_tools' function have been removed.

class PythonREPLInput(BaseModel):
    query: str = Field(description="The python code to execute.")

# NEW: A dedicated tool function for the Statistician
def get_statistician_tools():
    """Defines the tools for the statistician agent (just file writing)."""
    # We use the FileManagementToolkit to give it the write_file tool.
    # The reports will be saved in the 'output' directory.
    file_tools = FileManagementToolkit(
        root_dir="./output",
        selected_tools=["write_file"]
    ).get_tools()
    return file_tools

def get_analyst_tools(repl_tool: PythonREPLTool):
    """Defines the tools for the data analysis agent (unchanged)."""
    repl_tool.name = "python_code_interpreter"
    repl_tool.description = "A Python REPL for data analysis, calculations, and plotting. Always print results."
    repl_tool.args_schema = PythonREPLInput
    file_tools = FileManagementToolkit(
        root_dir=".",
        selected_tools=["read_file", "list_directory"]
    ).get_tools()
    return [repl_tool] + file_tools

# The get_writer_tools function is no longer needed and can be removed.