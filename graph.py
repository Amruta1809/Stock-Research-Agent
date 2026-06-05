from __future__ import annotations

import warnings
from typing import Any, Dict, List, TypedDict

with warnings.catch_warnings(record=True) as caught_warnings:
    warnings.simplefilter("always")
    from langgraph.graph import END, START, StateGraph

for warning in caught_warnings:
    message = str(warning.message)
    if "The default value of `allowed_objects` will change in a future version." in message:
        continue
    warnings.showwarning(
        warning.message,
        warning.category,
        warning.filename,
        warning.lineno,
        warning.file,
        warning.line,
    )


class StockState(TypedDict, total=False):
    ticker: str
    company_name: str
    raw_news: List[Dict[str, str]]
    sentiment_results: List[Dict[str, Any]]
    overall_sentiment: float
    sentiment_label: str
    bullish_count: int
    bearish_count: int
    neutral_count: int
    stock_df: Any
    metrics: Dict[str, Any]
    pattern_summary: str
    final_report: str
    recommendation: str


def news_node(state: StockState) -> StockState:
    from agents.news_agent import fetch_news_agent

    return fetch_news_agent(state)


def sentiment_node(state: StockState) -> StockState:
    from agents.sentiment_agent import analyze_sentiment_agent

    return analyze_sentiment_agent(state)


def pattern_node(state: StockState) -> StockState:
    from agents.pattern_agent import analyze_pattern_agent

    return analyze_pattern_agent(state)


def report_node(state: StockState) -> StockState:
    from agents.report_agent import generate_report_agent

    return generate_report_agent(state)


def build_graph():
    workflow = StateGraph(StockState)
    workflow.add_node("news_node", news_node)
    workflow.add_node("sentiment_node", sentiment_node)
    workflow.add_node("pattern_node", pattern_node)
    workflow.add_node("report_node", report_node)

    workflow.add_edge(START, "news_node")
    workflow.add_edge("news_node", "sentiment_node")
    workflow.add_edge("sentiment_node", "pattern_node")
    workflow.add_edge("pattern_node", "report_node")
    workflow.add_edge("report_node", END)

    return workflow.compile()


GRAPH = build_graph()


def run_pipeline(ticker: str, company_name: str) -> StockState:
    initial_state: StockState = {
        "ticker": ticker.upper(),
        "company_name": company_name,
        "raw_news": [],
        "sentiment_results": [],
        "overall_sentiment": 0.5,
        "sentiment_label": "Neutral",
        "bullish_count": 0,
        "bearish_count": 0,
        "neutral_count": 0,
        "stock_df": None,
        "metrics": {},
        "pattern_summary": "",
        "final_report": "",
        "recommendation": "🟡 HOLD",
    }
    return GRAPH.invoke(initial_state)
