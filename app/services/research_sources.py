import os
from urllib.parse import quote_plus
import feedparser
import requests
from .schemas import Paper, GitHubRepo

def search_arxiv(topic: str, max_results: int = 6):
    url = (
        "https://export.arxiv.org/api/query"
        f"?search_query=all:{quote_plus(topic)}"
        f"&start=0&max_results={max_results}"
        "&sortBy=submittedDate&sortOrder=descending"
    )
    try:
        feed = feedparser.parse(url)
        return [
            Paper(
                title=" ".join(e.title.split()),
                authors=", ".join(a.name for a in getattr(e, "authors", [])),
                published=getattr(e, "published", ""),
                url=getattr(e, "link", ""),
                relevance="Recent arXiv result related to the topic.",
            )
            for e in feed.entries
        ]
    except Exception:
        return []

def search_github(topic: str, max_results: int = 6):
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": topic, "sort": "updated", "order": "desc", "per_page": max_results},
            headers=headers,
            timeout=20,
        )
        r.raise_for_status()
        return [
            GitHubRepo(
                name=x["full_name"],
                url=x["html_url"],
                stars=x.get("stargazers_count", 0),
                description=x.get("description") or "",
                relevance="GitHub search result; verify implementation details before citing.",
            )
            for x in r.json().get("items", [])
        ]
    except Exception:
        return []
