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

def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""
    try:
        result = eval(expression)
        return str(result)
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error: {str(e)}"

TOOLS = {
    "search": {
        "function": search,
        "description": "Search the web for information. Input: a search query string"
    },
    "calculate": {
        "function": calculate,
        "description": "Calculate a mathematical expression. Input: a mathematical expression string like '2+2' or '10*5' or '2+2*3'"
    }
}

if __name__ == "__main__":
    print(search("What is the capital of France?"))
    print(calculate("41*90+3"))
