import json
from os import getenv
from typing import Optional
from tavily import TavilyClient

client = TavilyClient(api_key=getenv("TAVILY_API_KEY"))


def search_web(query: str) -> Optional[str]:
    """Use this function to search the web for a given query.
    This function is useful when you want an answer for a question that is not on hackernews.

    Args:
        query (str): Query to search for.

    Returns:
        str: JSON string of results related to the query.
    """

    search_result = client.search(query=query, search_depth="advanced")
    print(search_result)
    answer = []
    for result in search_result.get("results", []):
        answer.append(
            {
                "title": result["title"],
                "url": result["url"],
                "content": result["content"],
                "score": result["score"],
            }
        )
    return json.dumps(answer) if answer else "No results found."
