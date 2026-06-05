from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from graph import StockState
from utils.llm import run_chain
from utils.stock import get_stock_history, get_stock_info


template = """
You are a stock technical analyst.
Given these metrics for {ticker}:
- Current Price: {current_price}
- 6M Price Change: {price_change_6m}%
- 50-Day MA: {ma_50}
- 20-Day MA: {ma_20}
- Price Above 50MA: {above_ma50}
- RSI (14-day): {rsi}
- Annualized Volatility: {volatility}%
- Volume Trend: {volume_trend}

Write a 2-3 sentence plain English summary of the price pattern and technical outlook.
Be direct and factual.
"""


def _calculate_rsi(close_series: pd.Series) -> float:
    delta = close_series.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    latest = rsi.dropna()
    if latest.empty:
        return 50.0
    return float(latest.iloc[-1])


def _volume_trend(df: pd.DataFrame) -> str:
    if len(df) < 10:
        return "Insufficient data"
    recent_avg = df["Volume"].tail(5).mean()
    previous_avg = df["Volume"].tail(10).head(5).mean()
    if previous_avg == 0:
        return "Stable"
    change_pct = ((recent_avg - previous_avg) / previous_avg) * 100
    if change_pct > 5:
        return f"Increasing ({change_pct:.2f}%)"
    if change_pct < -5:
        return f"Decreasing ({change_pct:.2f}%)"
    return f"Stable ({change_pct:.2f}%)"


def _fallback_summary(ticker: str, metrics: Dict[str, Any]) -> str:
    direction = "above" if metrics["above_ma50"] else "below"
    return (
        f"{ticker} is trading {direction} its 50-day moving average with a "
        f"6-month move of {metrics['price_change_6m']:.2f}%. "
        f"RSI sits at {metrics['rsi']:.2f} and volume is {metrics['volume_trend'].lower()}."
    )


def analyze_pattern_agent(state: StockState) -> StockState:
    ticker = state["ticker"]
    stock_df = get_stock_history(ticker)
    company_info = get_stock_info(ticker)

    if stock_df.empty:
        metrics = {
            "current_price": 0.0,
            "price_change_6m": 0.0,
            "ma_50": 0.0,
            "ma_20": 0.0,
            "above_ma50": False,
            "rsi": 50.0,
            "volatility": 0.0,
            "volume_trend": "Insufficient data",
            "company_info": company_info,
        }
        return {
            **state,
            "stock_df": stock_df,
            "metrics": metrics,
            "pattern_summary": "Historical price data was unavailable, so technical analysis could not be completed.",
        }

    close_series = stock_df["Close"].dropna()
    current_price = float(close_series.iloc[-1])
    first_price = float(close_series.iloc[0])
    price_change_6m = ((current_price - first_price) / first_price) * 100 if first_price else 0.0
    ma_50 = float(close_series.rolling(50).mean().iloc[-1]) if len(close_series) >= 50 else current_price
    ma_20 = float(close_series.rolling(20).mean().iloc[-1]) if len(close_series) >= 20 else current_price
    above_ma50 = current_price > ma_50
    rsi = _calculate_rsi(close_series)
    volatility_value = float(close_series.pct_change().std() * (252**0.5) * 100)
    volatility = 0.0 if pd.isna(volatility_value) else round(volatility_value, 2)
    volume_trend = _volume_trend(stock_df)

    metrics = {
        "current_price": round(current_price, 2),
        "price_change_6m": round(price_change_6m, 2),
        "ma_50": round(ma_50, 2),
        "ma_20": round(ma_20, 2),
        "above_ma50": above_ma50,
        "rsi": round(rsi, 2),
        "volatility": volatility,
        "volume_trend": volume_trend,
        "company_info": company_info,
    }

    try:
        pattern_summary = run_chain(
            template=template,
            input_vars={
                "ticker": ticker,
                **metrics,
            },
        ).strip()
    except Exception:
        pattern_summary = _fallback_summary(ticker, metrics)

    return {
        **state,
        "stock_df": stock_df,
        "metrics": metrics,
        "pattern_summary": pattern_summary,
    }
