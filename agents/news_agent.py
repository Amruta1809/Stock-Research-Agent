from __future__ import annotations

from graph import StockState
from utils.search import search_news


def fetch_news_agent(state: StockState) -> StockState:
    ticker = state.get("ticker", "")
    company_name = state.get("company_name", "")
    query_subject = company_name or ticker
    raw_news = search_news(f"{query_subject} stock news today", max_results=5)
    return {**state, "raw_news": raw_news}
