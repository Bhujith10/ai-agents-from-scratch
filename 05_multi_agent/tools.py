from tavily import TavilyClient
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search(query: str) -> str:
    """Search the web for information."""
    response = tavily.search(query=query, max_results=2)
    formatted_results = []
    for result in response["results"]:
        formatted_results.append(
            f"📄 {result['content']}\n"
            f"🔗 Source: {result['url']}"
        )
    return "\n\n---\n\n".join(formatted_results)