"""
Web Search Tool
Uses Tavily API through LangChain's langchain-tavily package.
Returns search results with titles, snippets, and source URLs.
"""

import os
from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """
    Searches the web for current information.
    Use this when the user asks about recent news, events,
    or anything that requires up-to-date information.
    Returns titles, snippets, and source URLs.
    """
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key or api_key == "your_tavily_api_key_here":
        return "Error: TAVILY_API_KEY not set. Please add it to the .env file."

    try:
        from langchain_tavily import TavilySearch
        search = TavilySearch(max_results=3, tavily_api_key=api_key)
        results = search.invoke(query)
        return str(results)
    except Exception as e:
        return f"Error searching the web: {e}"
