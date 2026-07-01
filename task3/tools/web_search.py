"""Web search tool using Tavily via LangChain."""

import os
from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """
    Search the web for current information. Returns top results with
    titles, snippets, and source URLs.
    """
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key or api_key == "your_tavily_api_key_here":
        return "Error: TAVILY_API_KEY not set. Please add it to the .env file."

    try:
        from langchain_tavily import TavilySearch
        search = TavilySearch(max_results=3, tavily_api_key=api_key)
        raw = search.invoke(query)

        # Format results into clean readable text for the LLM
        results = raw if isinstance(raw, list) else raw.get("results", [])
        if not results:
            return "No results found."

        lines = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "No title")
            content = r.get("content", r.get("snippet", ""))
            url = r.get("url", "")
            lines.append(f"{i}. {title}\n   {content}\n   Source: {url}")

        return "\n\n".join(lines)

    except Exception as e:
        return f"Error searching the web: {e}"
