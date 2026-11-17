import requests

SEARCH_URL = "https://api.tavily.com/search"


class SearchError(Exception):
    """Raised when the web search fails. Never contains the API key."""


def web_search(query, api_key, max_results=5):
    """Return a list of {"title", "url", "content"} from Tavily."""
    try:
        r = requests.post(
            SEARCH_URL,
            headers={"Authorization": "Bearer " + api_key,
                     "Content-Type": "application/json"},
            json={"query": query[:400], "search_depth": "basic",
                  "max_results": max_results, "topic": "general"},
            timeout=15,
        )
    except requests.RequestException as e:
        raise SearchError(type(e).__name__) from None
    if r.status_code != 200:
        raise SearchError(f"HTTP {r.status_code}")
    try:
        data = r.json()
    except ValueError:
        raise SearchError("bad response") from None
    results = []
    for item in (data.get("results") or [])[:max_results]:
        url = item.get("url") or ""
        if not url.startswith("http"):
            continue
        results.append({
            "title": (item.get("title") or url)[:150],
            "url": url,
            "content": (item.get("content") or "")[:700],
        })
    return results