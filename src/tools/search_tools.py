import os
import json
import requests
from crewai.tools.base_tool import BaseTool
from typing import Dict, Any

class WebSearchCitationTool(BaseTool):
    name: str = "Web Search Citation Tool"
    description: str = (
        "Performs a web search for a given query and returns the top 5 results,"
        "each with a title, source URL (link), and a text snippet for citation"
    )

    def _run(self, query: str) -> list[dict] | str:
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Error: SERPER_API_KEY environment variable is not set"
        
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            response.raise_for_status()
            search_results = response.json().get("organic", [])

            if not search_results:
                return "No search results found"

            formatted_results = []
            for result in search_results[:5]:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                })

            return formatted_results
        except requests.exceptions.RequestException as e:
            return f"Error performing web search: {str(e)}"
        