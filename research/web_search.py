"""Optional web search. Search is user-triggered with /search, not automatic."""
def search_web(query: str, max_results: int = 5) -> list[dict[str, str]]:
    try:
        from ddgs import DDGS
    except ImportError as exc:
        raise RuntimeError("Web search package missing. Install requirements.txt first.") from exc

    with DDGS() as client:
        results = list(client.text(query, max_results=max_results))
    cleaned = []
    for item in results:
        cleaned.append({
            "title": str(item.get("title", "Untitled")),
            "url": str(item.get("href", "")),
            "snippet": str(item.get("body", "")),
        })
    return cleaned
