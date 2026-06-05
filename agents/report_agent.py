from __future__ import annotations

from graph import StockState
from utils.llm import run_chain


template = """
You are a senior financial research analyst.
Generate a structured research report based on this data:

Stock: {ticker} — {company_name}
Current Price: ${current_price}
6M Change: {price_change_6m}%
RSI: {rsi}
Above 50-Day MA: {above_ma50}
Volatility: {volatility}%
Sentiment: {sentiment_label} (score: {overall_sentiment}/1.0)
News Summary: {bullish_count} Bullish, {bearish_count} Bearish, {neutral_count} Neutral headlines
Pattern Analysis: {pattern_summary}

Write the report with EXACTLY these sections using these headers:
## Market Overview
## Sentiment Analysis
## Technical Analysis
## Risk Factors
## Recommendation: [BUY / HOLD / SELL]
## Reasoning

Keep each section concise (2-4 sentences or bullet points).
End with this exact line:
⚠️ Disclaimer: This is AI-generated analysis for educational purposes only. Not financial advice.
"""


def _fallback_report(state: StockState) -> str:
    metrics = state.get("metrics", {})
    recommendation = "HOLD"
    if state.get("sentiment_label") == "Bullish" and metrics.get("above_ma50"):
        recommendation = "BUY"
    elif state.get("sentiment_label") == "Bearish" and not metrics.get("above_ma50"):
        recommendation = "SELL"

    return f"""## Market Overview
{state['ticker']} is trading at ${metrics.get('current_price', 0.0):.2f} after a {metrics.get('price_change_6m', 0.0):.2f}% move over the last six months.
Recent coverage volume is modest, and the pipeline combines that news flow with price action for a quick directional read.

## Sentiment Analysis
Headline sentiment is {state.get('sentiment_label', 'Neutral').lower()} with {state.get('bullish_count', 0)} bullish, {state.get('bearish_count', 0)} bearish, and {state.get('neutral_count', 0)} neutral items.
The aggregate sentiment score is {state.get('overall_sentiment', 0.5):.2f} on a 0 to 1 scale.

## Technical Analysis
RSI is {metrics.get('rsi', 50.0):.2f}, volatility is {metrics.get('volatility', 0.0):.2f}%, and price is {'above' if metrics.get('above_ma50') else 'below'} the 50-day moving average.
{state.get('pattern_summary', 'No technical summary was generated.')}

## Risk Factors
Short-term signals can reverse quickly when driven by a small set of headlines or volatile macro conditions.
Historical price patterns and headline sentiment should be validated with deeper fundamental research before any decision.

## Recommendation: {recommendation}
The combined signals support a {recommendation.lower()} stance based on the current sentiment and technical snapshot.

## Reasoning
This recommendation leans on recent headline tone, trend positioning versus moving averages, momentum via RSI, and realized volatility.
If sentiment or price trend changes materially, the conclusion should be revisited.

⚠️ Disclaimer: This is AI-generated analysis for educational purposes only. Not financial advice."""


def generate_report_agent(state: StockState) -> StockState:
    metrics = state.get("metrics", {})
    payload = {
        "ticker": state.get("ticker", ""),
        "company_name": state.get("company_name", ""),
        "current_price": metrics.get("current_price", 0.0),
        "price_change_6m": metrics.get("price_change_6m", 0.0),
        "rsi": metrics.get("rsi", 50.0),
        "above_ma50": metrics.get("above_ma50", False),
        "volatility": metrics.get("volatility", 0.0),
        "sentiment_label": state.get("sentiment_label", "Neutral"),
        "overall_sentiment": round(state.get("overall_sentiment", 0.5), 2),
        "bullish_count": state.get("bullish_count", 0),
        "bearish_count": state.get("bearish_count", 0),
        "neutral_count": state.get("neutral_count", 0),
        "pattern_summary": state.get("pattern_summary", ""),
    }

    try:
        final_report = run_chain(template=template, input_vars=payload).strip()
    except Exception:
        final_report = _fallback_report(state)

    normalized_report = final_report.upper()
    if "BUY" in normalized_report:
        recommendation = "🟢 BUY"
    elif "SELL" in normalized_report:
        recommendation = "🔴 SELL"
    else:
        recommendation = "🟡 HOLD"

    return {
        **state,
        "final_report": final_report,
        "recommendation": recommendation,
    }
