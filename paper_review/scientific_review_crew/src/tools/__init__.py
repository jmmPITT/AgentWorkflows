"""
Tools for Elite Scientific Review Crew

This module contains specialized tools for PDF processing and web search verification.
"""

from .pdf_tools import PDFTool
from .search_tools import WebSearchCitationTool

__all__ = [
    "PDFTool",
    "WebSearchCitationTool"
]
