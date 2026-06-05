from __future__ import annotations

import time
from typing import Any, Dict

import pandas as pd
import yfinance as yf

try:
    from yfinance.exceptions import YFRateLimitError
except Exception:  # pragma: no cover - version compatibility
    YFRateLimitError = Exception


_CACHE_TTL_SECONDS = 15 * 60
_EMPTY_HISTORY = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])
_history_cache: Dict[tuple[str, str], tuple[float, pd.DataFrame]] = {}
_info_cache: Dict[str, tuple[float, Dict[str, Any]]] = {}


def _is_cache_fresh(timestamp: float) -> bool:
    return (time.time() - timestamp) < _CACHE_TTL_SECONDS


def _is_rate_limited_error(exc: Exception) -> bool:
    return isinstance(exc, YFRateLimitError) or "Too Many Requests" in str(exc)


def _get_cached_history(ticker: str, period: str) -> pd.DataFrame | None:
    cached = _history_cache.get((ticker, period))
    if not cached:
        return None
    timestamp, df = cached
    if not _is_cache_fresh(timestamp):
        return None
    return df.copy()


def _get_cached_info(ticker: str) -> Dict[str, Any] | None:
    cached = _info_cache.get(ticker)
    if not cached:
        return None
    timestamp, info = cached
    if not _is_cache_fresh(timestamp):
        return None
    return dict(info)


def _store_history_cache(ticker: str, period: str, df: pd.DataFrame) -> None:
    _history_cache[(ticker, period)] = (time.time(), df.copy())


def _store_info_cache(ticker: str, info: Dict[str, Any]) -> None:
    _info_cache[ticker] = (time.time(), dict(info))


def get_stock_history(ticker: str, period: str = "6mo") -> pd.DataFrame:
    cached_history = _get_cached_history(ticker, period)
    if cached_history is not None:
        return cached_history

    last_error: Exception | None = None
    for attempt in range(3):
        try:
            history = yf.Ticker(ticker).history(period=period)
            if history.empty:
                return _EMPTY_HISTORY.copy()
            formatted_history = history.reset_index(drop=False)
            _store_history_cache(ticker, period, formatted_history)
            return formatted_history
        except Exception as exc:
            last_error = exc
            if _is_rate_limited_error(exc):
                fallback_history = _get_cached_history(ticker, period)
                if fallback_history is not None:
                    return fallback_history
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))

    if last_error and _is_rate_limited_error(last_error):
        return _EMPTY_HISTORY.copy()
    return _EMPTY_HISTORY.copy()


def get_stock_info(ticker: str) -> Dict[str, Any]:
    cached_info = _get_cached_info(ticker)
    if cached_info is not None:
        return cached_info

    last_error: Exception | None = None
    for attempt in range(2):
        try:
            info = yf.Ticker(ticker).info
            if isinstance(info, dict) and info:
                _store_info_cache(ticker, info)
                return info
            return {}
        except Exception as exc:
            last_error = exc
            if _is_rate_limited_error(exc):
                fallback_info = _get_cached_info(ticker)
                if fallback_info is not None:
                    return fallback_info
            if attempt < 1:
                time.sleep(1.0)

    if last_error and _is_rate_limited_error(last_error):
        return {}
    return {}
