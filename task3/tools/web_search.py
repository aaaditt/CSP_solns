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

        # TavilySearch can return different shapes depending on version:
        # - A list of {'type': 'text', 'text': '...'} blocks
        # - A list of {'title': ..., 'content': ..., 'url': ...} dicts
        # - A dict with a 'results' key

        if isinstance(raw, list):
            parts = []
            for item in raw:
                if isinstance(item, dict):
                    if "text" in item:
                        # Content-block format
                        parts.append(item["text"])
                    elif "content" in item:
                        # Standard result format
                        title = item.get("title", "")
                        content = item.get("content", "")
                        url = item.get("url", "")
                        entry = f"{title}\n{content}"
                        if url:
                            entry += f"\nSource: {url}"
                        parts.append(entry)
            return "\n\n".join(parts) if parts else str(raw)

        if isinstance(raw, dict):
            results = raw.get("results", [])
            if results:
                parts = []
                for r in results:
                    title = r.get("title", "")
                    content = r.get("content", r.get("snippet", ""))
                    url = r.get("url", "")
                    entry = f"{title}\n{content}"
                    if url:
                        entry += f"\nSource: {url}"
                    parts.append(entry)
                return "\n\n".join(parts)
            return raw.get("answer", str(raw))

        return str(raw)

    except Exception as e:
        return f"Error searching the web: {e}"
