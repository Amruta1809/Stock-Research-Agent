from __future__ import annotations

import pandas as pd

from agents.sentiment_agent import analyze_sentiment_agent
from graph import run_pipeline


def test_sentiment_agent_parses_model_output(monkeypatch):
    def fake_run_chain(template, input_vars):
        return """
        [
          {"headline": "Stock rallies on earnings beat", "sentiment": "Bullish", "score": 0.82, "reason": "Strong earnings support upside."},
          {"headline": "Analysts flag valuation concerns", "sentiment": "Bearish", "score": 0.21, "reason": "Valuation concerns can pressure sentiment."}
        ]
        """

    monkeypatch.setattr("agents.sentiment_agent.run_chain", fake_run_chain)

    state = analyze_sentiment_agent(
        {
            "raw_news": [
                {"title": "Stock rallies on earnings beat"},
                {"title": "Analysts flag valuation concerns"},
            ]
        }
    )

    assert state["bullish_count"] == 1
    assert state["bearish_count"] == 1
    assert state["neutral_count"] == 0
    assert state["sentiment_label"] == "Neutral"
    assert len(state["sentiment_results"]) == 2


def test_run_pipeline_with_monkeypatched_agents(monkeypatch):
    fake_df = pd.DataFrame(
        {
            "Close": [100 + i for i in range(60)],
            "Volume": [1_000_000 + (i * 1_000) for i in range(60)],
        }
    )

    def fake_news_agent(state):
        return {
            **state,
            "raw_news": [
                {"title": "Apple expands AI features", "url": "https://example.com/1", "snippet": "Product momentum improves."},
                {"title": "Services growth remains steady", "url": "https://example.com/2", "snippet": "Recurring revenue continues."},
            ],
        }

    def fake_sentiment_agent(state):
        return {
            **state,
            "sentiment_results": [
                {"headline": "Apple expands AI features", "sentiment": "Bullish", "score": 0.8, "reason": "Expansion is positive."},
                {"headline": "Services growth remains steady", "sentiment": "Bullish", "score": 0.75, "reason": "Stable growth helps sentiment."},
            ],
            "overall_sentiment": 0.775,
            "sentiment_label": "Bullish",
            "bullish_count": 2,
            "bearish_count": 0,
            "neutral_count": 0,
        }

    def fake_pattern_agent(state):
        return {
            **state,
            "stock_df": fake_df,
            "metrics": {
                "current_price": 159.0,
                "price_change_6m": 59.0,
                "ma_50": 134.5,
                "ma_20": 149.5,
                "above_ma50": True,
                "rsi": 62.4,
                "volatility": 18.2,
                "volume_trend": "Increasing (4.50%)",
            },
            "pattern_summary": "Momentum is constructive and the trend remains intact.",
        }

    def fake_report_agent(state):
        return {
            **state,
            "final_report": """## Market Overview
Momentum remains healthy.
## Sentiment Analysis
News tone is positive.
## Technical Analysis
Trend is supportive.
## Risk Factors
Valuation could tighten upside.
## Recommendation: BUY
Constructive setup.
## Reasoning
Signals are aligned.

⚠️ Disclaimer: This is AI-generated analysis for educational purposes only. Not financial advice.""",
            "recommendation": "🟢 BUY",
        }

    monkeypatch.setattr("agents.news_agent.fetch_news_agent", fake_news_agent)
    monkeypatch.setattr("agents.sentiment_agent.analyze_sentiment_agent", fake_sentiment_agent)
    monkeypatch.setattr("agents.pattern_agent.analyze_pattern_agent", fake_pattern_agent)
    monkeypatch.setattr("agents.report_agent.generate_report_agent", fake_report_agent)

    state = run_pipeline("AAPL", "Apple Inc.")

    assert state["ticker"] == "AAPL"
    assert state["company_name"] == "Apple Inc."
    assert state["recommendation"] == "🟢 BUY"
    assert state["sentiment_label"] == "Bullish"
    assert state["metrics"]["above_ma50"] is True
    assert len(state["raw_news"]) == 2
