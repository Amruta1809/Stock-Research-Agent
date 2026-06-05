from __future__ import annotations

import warnings
from typing import Dict, List

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS


def search_news(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"This package \(`duckduckgo_search`\) has been renamed to `ddgs`!.*",
                category=RuntimeWarning,
            )
            ddgs = DDGS()
        with ddgs:
            try:
                items = ddgs.news(query, max_results=max_results)
            except Exception:
                items = ddgs.text(query, max_results=max_results)

            for item in items:
                results.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("href", ""),
                        "snippet": item.get("body", ""),
                    }
                )
                if len(results) >= max_results:
                    break
    except Exception:
        return []
    return results
