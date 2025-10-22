"""
Basic tests for Elite Scientific Review Crew
"""

import pytest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that all modules can be imported without errors"""
    try:
        from agents import get_agents, create_specialist_agent
        from tasks import get_tasks, create_analysis_task
        from crew import assemble_crew
        from tools.pdf_tools import PDFTool
        from tools.search_tools import WebSearchCitationTool
        assert True
    except ImportError as e:
        pytest.fail(f"Import error: {e}")

def test_agent_creation():
    """Test that agent creation function exists and has correct signature"""
    from agents import create_specialist_agent
    import inspect
    
    # Check function signature
    sig = inspect.signature(create_specialist_agent)
    params = list(sig.parameters.keys())
    
    assert "domain" in params
    assert "llm_instance" in params
    assert len(params) == 2

def test_pdf_tool():
    """Test PDF tool initialization"""
    from tools.pdf_tools import PDFTool
    
    pdf_tool = PDFTool()
    assert pdf_tool.name == "Page-Based PDF Processor"
    assert pdf_tool.description is not None

def test_search_tool():
    """Test search tool initialization"""
    from tools.search_tools import WebSearchCitationTool
    
    search_tool = WebSearchCitationTool()
    assert search_tool.name == "Web Search Citation Tool"
    assert search_tool.description is not None

def test_environment_variables():
    """Test that required environment variables are documented"""
    # This test ensures we have proper documentation
    # The actual environment setup is tested in integration tests
    required_vars = ["GCP_PROJECT_ID", "GCP_REGION", "SERPER_API_KEY"]
    
    # Check if env.example exists and contains required variables
    env_example_path = os.path.join(os.path.dirname(__file__), '..', 'env.example')
    assert os.path.exists(env_example_path), "env.example file should exist"
    
    with open(env_example_path, 'r') as f:
        content = f.read()
        for var in required_vars:
            assert var in content, f"{var} should be documented in env.example"

if __name__ == "__main__":
    pytest.main([__file__])
