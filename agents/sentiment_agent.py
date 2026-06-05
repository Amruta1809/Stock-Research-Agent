from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from graph import StockState
from utils.llm import run_chain


template = """
You are a financial sentiment analyzer.
Analyze each news headline below and classify as Bullish, Bearish, or Neutral.
Use the score as a directional sentiment score where:
- 0.0 = strongly bearish
- 0.5 = neutral
- 1.0 = strongly bullish
Return ONLY a valid JSON array. No markdown. No explanation. No backticks.

Format:
[
  {{
    "headline": "...",
    "sentiment": "Bullish/Bearish/Neutral",
    "score": 0.0 to 1.0,
    "reason": "one sentence"
  }}
]

Headlines:
{headlines}
"""

BULLISH_KEYWORDS = {
    "beat",
    "beats",
    "growth",
    "surge",
    "rally",
    "upgrade",
    "upside",
    "profit",
    "profits",
    "record",
    "strong",
    "expands",
    "expansion",
    "gain",
    "gains",
    "bullish",
    "optimistic",
    "outperform",
}

BEARISH_KEYWORDS = {
    "miss",
    "misses",
    "drop",
    "falls",
    "fall",
    "downgrade",
    "lawsuit",
    "probe",
    "cuts",
    "cut",
    "weak",
    "decline",
    "declines",
    "loss",
    "losses",
    "bearish",
    "warning",
    "risk",
    "risks",
    "concern",
    "concerns",
    "slump",
}


def _safe_json_array(payload: str) -> List[Dict[str, Any]]:
    try:
        parsed = json.loads(payload)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        match = re.search(r"\[[\s\S]*\]", payload)
        if not match:
            return []
        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []


def _coerce_sentiment(value: Any) -> str:
    normalized = str(value or "Neutral").strip().lower()
    if normalized == "bullish":
        return "Bullish"
    if normalized == "bearish":
        return "Bearish"
    return "Neutral"


def _coerce_score(value: Any) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        score = -1.0
    return max(0.0, min(1.0, score))


def _keyword_bias(text: str) -> int:
    lowered = text.lower()
    bullish_hits = sum(1 for keyword in BULLISH_KEYWORDS if keyword in lowered)
    bearish_hits = sum(1 for keyword in BEARISH_KEYWORDS if keyword in lowered)
    return bullish_hits - bearish_hits


def _heuristic_sentiment(headline: str) -> Dict[str, Any]:
    bias = _keyword_bias(headline)
    if bias > 0:
        sentiment = "Bullish"
        score = min(0.9, 0.65 + (0.05 * bias))
        reason = "Positive keywords in the headline suggest constructive market sentiment."
    elif bias < 0:
        sentiment = "Bearish"
        score = max(0.1, 0.35 + (0.05 * bias))
        reason = "Negative keywords in the headline suggest cautious market sentiment."
    else:
        sentiment = "Neutral"
        score = 0.5
        reason = "The headline appears informational without a strong directional signal."

    return {
        "headline": headline,
        "sentiment": sentiment,
        "score": round(score, 2),
        "reason": reason,
    }


def _directional_score(sentiment: str, headline: str, reason: str, raw_score: float) -> float:
    keyword_adjustment = max(-0.15, min(0.15, _keyword_bias(f"{headline} {reason}") * 0.04))

    if sentiment == "Bullish":
        base_score = 0.7
        if raw_score >= 0.5:
            base_score = max(base_score, raw_score)
        return round(min(1.0, base_score + max(0.0, keyword_adjustment)), 2)

    if sentiment == "Bearish":
        base_score = 0.3
        if 0.0 <= raw_score <= 0.5:
            base_score = min(base_score, raw_score)
        return round(max(0.0, base_score + min(0.0, keyword_adjustment)), 2)

    return 0.5


def analyze_sentiment_agent(state: StockState) -> StockState:
    raw_news = state.get("raw_news", [])
    if not raw_news:
        return {
            **state,
            "sentiment_results": [],
            "overall_sentiment": 0.5,
            "sentiment_label": "Neutral",
            "bullish_count": 0,
            "bearish_count": 0,
            "neutral_count": 0,
        }

    headlines = "\n".join(
        f"{index}. {item.get('title', '')}" for index, item in enumerate(raw_news, start=1)
    )

    try:
        response = run_chain(template=template, input_vars={"headlines": headlines})
        parsed_results = _safe_json_array(response)
    except Exception:
        parsed_results = []

    if not parsed_results:
        parsed_results = [
            _heuristic_sentiment(item.get("title", ""))
            for item in raw_news
        ]

    sentiment_results: List[Dict[str, Any]] = []
    bullish_count = 0
    bearish_count = 0
    neutral_count = 0

    for index, result in enumerate(parsed_results):
        source_headline = raw_news[index]["title"] if index < len(raw_news) else ""
        sentiment = _coerce_sentiment(result.get("sentiment"))
        reason = result.get("reason", "")
        raw_score = _coerce_score(result.get("score"))
        score = _directional_score(
            sentiment=sentiment,
            headline=result.get("headline") or source_headline,
            reason=reason,
            raw_score=raw_score,
        )
        cleaned_result = {
            "headline": result.get("headline") or source_headline,
            "sentiment": sentiment,
            "score": score,
            "reason": reason,
        }
        sentiment_results.append(cleaned_result)

        if sentiment == "Bullish":
            bullish_count += 1
        elif sentiment == "Bearish":
            bearish_count += 1
        else:
            neutral_count += 1

    if len(sentiment_results) < len(raw_news):
        for item in raw_news[len(sentiment_results) :]:
            fallback_result = _heuristic_sentiment(item.get("title", ""))
            sentiment_results.append(fallback_result)
            if fallback_result["sentiment"] == "Bullish":
                bullish_count += 1
            elif fallback_result["sentiment"] == "Bearish":
                bearish_count += 1
            else:
                neutral_count += 1

    if sentiment_results and all(item["sentiment"] == "Neutral" for item in sentiment_results):
        sentiment_results = [
            _heuristic_sentiment(item.get("title", ""))
            for item in raw_news
        ]
        bullish_count = sum(1 for item in sentiment_results if item["sentiment"] == "Bullish")
        bearish_count = sum(1 for item in sentiment_results if item["sentiment"] == "Bearish")
        neutral_count = sum(1 for item in sentiment_results if item["sentiment"] == "Neutral")

    overall_sentiment = sum(item["score"] for item in sentiment_results) / len(sentiment_results)
    if bullish_count > 0 and bearish_count > 0 and 0.4 <= overall_sentiment <= 0.6:
        sentiment_label = "Mixed"
    elif overall_sentiment > 0.6:
        sentiment_label = "Bullish"
    elif overall_sentiment < 0.4:
        sentiment_label = "Bearish"
    else:
        sentiment_label = "Neutral"

    return {
        **state,
        "sentiment_results": sentiment_results,
        "overall_sentiment": overall_sentiment,
        "sentiment_label": sentiment_label,
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "neutral_count": neutral_count,
    }
