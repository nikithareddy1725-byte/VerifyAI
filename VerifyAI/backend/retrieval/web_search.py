class WebSearcher:
    def search(self, query: str, num_results: int = 5) -> list[dict]:
        # Local fallback since web search API is not configured
        return [
            {
                "title": "Search Unavailable",
                "link": "http://localhost",
                "snippet": f"Web search is not configured. Could not search for: {query}"
            }
        ]
