from __future__ import annotations

import html

import streamlit as st

from charts.visualizations import create_price_chart, create_volume_chart
from graph import run_pipeline


st.set_page_config(
    page_title="Stock Research Agent",
    page_icon="favicon.png",
    layout="wide",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Source+Serif+4:wght@400;600&display=swap');

        :root {
            --bg: #07111f;
            --panel: rgba(14, 28, 46, 0.88);
            --panel-soft: rgba(15, 37, 61, 0.72);
            --panel-border: rgba(255, 255, 255, 0.08);
            --text: #f4efe6;
            --muted: #9ca9bd;
            --accent: #ffb84d;
            --accent-strong: #ff7a3d;
            --mint: #40d8a6;
            --rose: #ff7f8e;
            --ice: #7cc7ff;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(255, 184, 77, 0.12), transparent 26%),
                radial-gradient(circle at top right, rgba(64, 216, 166, 0.10), transparent 24%),
                linear-gradient(180deg, #09111d 0%, #07111f 58%, #06101c 100%);
            color: var(--text);
            font-family: "Space Grotesk", "Trebuchet MS", sans-serif;
        }

        [data-testid="stHeader"] {
            background: rgba(7, 17, 31, 0.35);
        }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(17, 27, 42, 0.96) 0%, rgba(12, 20, 33, 0.98) 100%);
            border-right: 1px solid var(--panel-border);
        }

        [data-testid="stSidebar"] .block-container {
            padding-top: 2rem;
        }

        .block-container {
            padding-top: 2.2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            color: var(--text);
            font-family: "Space Grotesk", "Trebuchet MS", sans-serif;
            letter-spacing: -0.03em;
        }

        .hero-card {
            background:
                linear-gradient(135deg, rgba(21, 42, 68, 0.92), rgba(9, 18, 31, 0.90)),
                linear-gradient(90deg, rgba(255, 184, 77, 0.08), transparent);
            border: 1px solid var(--panel-border);
            border-radius: 28px;
            padding: 2rem 2.2rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 24px 80px rgba(0, 0, 0, 0.24);
            overflow: hidden;
        }

        .hero-kicker {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: rgba(255, 184, 77, 0.14);
            color: #ffd28f;
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 1rem;
        }

        .hero-title {
            font-size: 3.2rem;
            line-height: 0.95;
            margin: 0;
            max-width: 10ch;
        }

        .hero-copy {
            color: var(--muted);
            max-width: 56ch;
            margin-top: 1rem;
            font-size: 1.03rem;
        }

        .hero-summary {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.9rem;
            margin-top: 1.35rem;
        }

        .hero-summary-card {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 18px;
            padding: 0.95rem 1rem;
        }

        .hero-summary-label {
            color: var(--muted);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .hero-summary-value {
            font-size: 1.15rem;
            margin-top: 0.2rem;
        }

        .sidebar-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 22px;
            padding: 1.15rem;
            margin-bottom: 1rem;
        }

        .sidebar-title {
            margin: 0 0 0.3rem 0;
            font-size: 1.4rem;
        }

        .sidebar-copy {
            color: var(--muted);
            font-size: 0.92rem;
            margin-bottom: 0.6rem;
        }

        .pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.75rem;
        }

        .pill {
            display: inline-flex;
            padding: 0.3rem 0.65rem;
            border-radius: 999px;
            background: rgba(124, 199, 255, 0.12);
            border: 1px solid rgba(124, 199, 255, 0.16);
            color: #cfe8ff;
            font-size: 0.82rem;
        }

        .metric-card {
            background: linear-gradient(180deg, rgba(18, 34, 55, 0.94), rgba(12, 24, 39, 0.94));
            border: 1px solid var(--panel-border);
            border-radius: 22px;
            padding: 1.15rem 1.2rem;
            min-height: 148px;
            margin-top: 0.35rem;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.65rem;
        }

        .metric-value {
            font-size: 2.15rem;
            line-height: 1;
            color: var(--text);
            margin-bottom: 0.45rem;
        }

        .metric-subtext {
            color: var(--muted);
            font-size: 0.96rem;
        }

        .recommendation-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.35rem 0.78rem;
            border-radius: 999px;
            background: rgba(255, 184, 77, 0.16);
            color: #ffd28f;
            font-size: 0.9rem;
            margin-bottom: 0.8rem;
        }

        .panel-card {
            background: linear-gradient(180deg, rgba(15, 28, 45, 0.92), rgba(10, 20, 33, 0.92));
            border: 1px solid var(--panel-border);
            border-radius: 24px;
            padding: 1.3rem;
            margin-top: 1rem;
        }

        .section-label {
            color: var(--muted);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.35rem;
        }

        .body-copy {
            color: #d7deea;
            font-size: 1rem;
            line-height: 1.7;
        }

        .body-copy p, .body-copy li {
            color: #d7deea;
            font-family: "Source Serif 4", Georgia, serif;
        }

        .news-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 20px;
            padding: 1rem 1.05rem;
            margin-bottom: 0.85rem;
        }

        .news-kicker {
            color: var(--accent);
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.25rem;
        }

        .news-title a {
            color: var(--text);
            text-decoration: none;
            font-size: 1.06rem;
            font-weight: 600;
        }

        .news-title a:hover {
            color: #ffd28f;
        }

        .news-snippet {
            color: var(--muted);
            margin-top: 0.45rem;
            line-height: 1.6;
        }

        .sentiment-item {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.9rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }

        .sentiment-item:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }

        .sentiment-title {
            color: var(--text);
            font-size: 0.98rem;
            margin-bottom: 0.28rem;
        }

        .sentiment-reason {
            color: var(--muted);
            font-size: 0.92rem;
            line-height: 1.5;
        }

        .sentiment-badge {
            min-width: 96px;
            text-align: center;
            padding: 0.45rem 0.68rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .sentiment-bullish {
            background: rgba(64, 216, 166, 0.14);
            color: #8cf0cb;
        }

        .sentiment-bearish {
            background: rgba(255, 127, 142, 0.14);
            color: #ffb4bf;
        }

        .sentiment-neutral, .sentiment-mixed {
            background: rgba(124, 199, 255, 0.14);
            color: #cfe8ff;
        }

        .empty-state {
            background: linear-gradient(180deg, rgba(14, 29, 47, 0.94), rgba(11, 21, 34, 0.92));
            border: 1px dashed rgba(255, 255, 255, 0.12);
            border-radius: 28px;
            padding: 2rem;
            margin-top: 1rem;
        }

        .empty-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin-top: 1.25rem;
        }

        .empty-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 20px;
            padding: 1rem;
        }

        .empty-card-title {
            color: var(--text);
            font-size: 1rem;
            margin-bottom: 0.35rem;
        }

        .empty-card-copy {
            color: var(--muted);
            font-size: 0.93rem;
            line-height: 1.55;
        }

        @media (max-width: 900px) {
            .hero-title {
                font-size: 2.5rem;
            }

            .hero-summary,
            .empty-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, subtext: str = "") -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-subtext">{subtext}</div>
    </div>
    """


def render_sidebar() -> tuple[str, str, bool]:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-card">
                <div class="sidebar-title">Research Controls</div>
                <div class="sidebar-copy">
                    Pick a ticker, pair it with the company name used in news coverage,
                    and generate a fresh multi-agent market brief.
                </div>
                <div class="pill-row">
                    <span class="pill">Live headlines</span>
                    <span class="pill">Sentiment read</span>
                    <span class="pill">6M technicals</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("research_form", clear_on_submit=False):
            ticker = st.text_input("Ticker", value="AAPL").strip().upper()
            company_name = st.text_input("Company Name", value="Apple Inc.").strip()
            run_analysis = st.form_submit_button(
                "Run Analysis",
                type="primary",
                use_container_width=True,
            )

        st.markdown(
            """
            <div class="sidebar-card">
                <div class="section-label">Starter Ideas</div>
                <div class="body-copy">
                    Try <strong>TSLA</strong>, <strong>NVDA</strong>, <strong>INTC</strong>,
                    or <strong>BA</strong> for more varied headline tone.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Set `OPENROUTER_API_KEY` in `.env` before running the app.")

    return ticker, company_name, run_analysis


def sentiment_class(label: str) -> str:
    normalized = label.lower()
    if normalized == "bullish":
        return "sentiment-bullish"
    if normalized == "bearish":
        return "sentiment-bearish"
    if normalized == "mixed":
        return "sentiment-mixed"
    return "sentiment-neutral"


def render_hero(state: dict, ticker: str, company_name: str) -> None:
    metrics = state.get("metrics", {})
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-kicker">Market Brief • {ticker}</div>
            <h1 class="hero-title">{company_name}</h1>
            <div class="hero-copy">
                A stitched-together view of recent headlines, sentiment flow, and
                six-month price behavior for faster first-pass research.
            </div>
            <div class="hero-summary">
                <div class="hero-summary-card">
                    <div class="hero-summary-label">Recommendation</div>
                    <div class="hero-summary-value">{state.get("recommendation", "🟡 HOLD")}</div>
                </div>
                <div class="hero-summary-card">
                    <div class="hero-summary-label">Sentiment Pulse</div>
                    <div class="hero-summary-value">{state.get("sentiment_label", "Neutral")}</div>
                </div>
                <div class="hero-summary-card">
                    <div class="hero-summary-label">Volume Trend</div>
                    <div class="hero-summary-value">{metrics.get("volume_trend", "Unavailable")}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sentiment_breakdown(sentiment_results: list[dict]) -> None:
    st.markdown('<div class="section-label">Headline Sentiment</div>', unsafe_allow_html=True)
    if not sentiment_results:
        st.info("No sentiment results available.")
        return

    items: list[str] = []
    for item in sentiment_results:
        label = item.get("sentiment", "Neutral")
        items.append(
            "".join(
                [
                    '<div class="sentiment-item">',
                    "<div>",
                    f'<div class="sentiment-title">{html.escape(item.get("headline", ""))}</div>',
                    f'<div class="sentiment-reason">{html.escape(item.get("reason", ""))}</div>',
                    "</div>",
                    f'<div class="sentiment-badge {sentiment_class(label)}">',
                    f'{html.escape(label)} · {item.get("score", 0.5):.2f}',
                    "</div>",
                    "</div>",
                ]
            )
        )
    st.markdown(
        f'<div class="panel-card">{"".join(items)}</div>',
        unsafe_allow_html=True,
    )


def render_news(raw_news: list[dict]) -> None:
    st.markdown('<div class="section-label">Recent News</div>', unsafe_allow_html=True)
    if not raw_news:
        st.info("No recent news articles were found.")
        return

    for index, item in enumerate(raw_news, start=1):
        st.markdown(
            f"""
            <div class="news-card">
                <div class="news-kicker">Headline {index}</div>
                <div class="news-title"><a href="{item.get('url', '#')}" target="_blank">{html.escape(item.get('title', ''))}</a></div>
                <div class="news-snippet">{html.escape(item.get('snippet', ''))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-kicker">Stock Research Agent</div>
            <h1 class="hero-title">A cleaner first read on any public company.</h1>
            <div class="hero-copy">
                Run the workflow from the left panel to combine live news, sentiment,
                historical price action, and an AI-generated research note in one place.
            </div>
        </div>
        <div class="empty-state">
            <div class="section-label">What You Get</div>
            <div class="empty-grid">
                <div class="empty-card">
                    <div class="empty-card-title">Signal Snapshot</div>
                    <div class="empty-card-copy">Recommendation, price move, sentiment pulse, RSI, and volatility surfaced as quick-read cards.</div>
                </div>
                <div class="empty-card">
                    <div class="empty-card-title">Visual Trend Read</div>
                    <div class="empty-card-copy">Moving averages and volume are shown in dedicated market panels so the technical story is easy to scan.</div>
                </div>
                <div class="empty-card">
                    <div class="empty-card-title">News Context</div>
                    <div class="empty-card-copy">Recent headlines and per-headline sentiment reasons stay alongside the report, instead of buried in a raw table.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_report_html(report: str) -> str:
    parts: list[str] = []
    in_list = False

    for raw_line in report.splitlines():
        line = raw_line.strip()
        if not line:
            if in_list:
                parts.append("</ul>")
                in_list = False
            continue
        if line.startswith("## "):
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f"<h3>{html.escape(line[3:])}</h3>")
            continue
        if line.startswith("- "):
            if not in_list:
                parts.append("<ul>")
                in_list = True
            parts.append(f"<li>{html.escape(line[2:])}</li>")
            continue
        if in_list:
            parts.append("</ul>")
            in_list = False
        if line.startswith("Disclaimer:") or line.startswith("⚠"):
            parts.append(f"<p><em>{html.escape(line)}</em></p>")
        else:
            parts.append(f"<p>{html.escape(line)}</p>")

    if in_list:
        parts.append("</ul>")

    return "".join(parts)


def format_copy_html(text: str) -> str:
    paragraphs = [segment.strip() for segment in text.splitlines() if segment.strip()]
    return "".join(f"<p>{html.escape(paragraph)}</p>" for paragraph in paragraphs)


inject_styles()
ticker, company_name, run_analysis = render_sidebar()

if "analysis_state" not in st.session_state:
    st.session_state.analysis_state = None
if "analysis_meta" not in st.session_state:
    st.session_state.analysis_meta = {"ticker": "", "company_name": ""}

if run_analysis:
    if not ticker or not company_name:
        st.error("Please provide both a ticker and company name.")
    else:
        with st.spinner(f"Researching {ticker}..."):
            try:
                state = run_pipeline(ticker=ticker, company_name=company_name)
            except Exception as exc:  # pragma: no cover - Streamlit UI
                st.exception(exc)
                st.stop()

        st.session_state.analysis_state = state
        st.session_state.analysis_meta = {
            "ticker": ticker,
            "company_name": company_name,
        }

state = st.session_state.analysis_state
meta = st.session_state.analysis_meta

if not state:
    render_empty_state()
else:
    metrics = state.get("metrics", {})
    stock_df = state.get("stock_df")
    raw_news = state.get("raw_news", [])
    sentiment_results = state.get("sentiment_results", [])

    current_price = metrics.get("current_price", 0.0)
    price_change = metrics.get("price_change_6m", 0.0)
    recommendation = state.get("recommendation", "🟡 HOLD")
    sentiment_label = state.get("sentiment_label", "Neutral")
    overall_sentiment = state.get("overall_sentiment", 0.5)

    render_hero(state, meta["ticker"], meta["company_name"])

    metric_cols = st.columns(4)
    metric_cols[0].markdown(
        metric_card("Recommendation", recommendation, f"Headline tone: {sentiment_label}"),
        unsafe_allow_html=True,
    )
    metric_cols[1].markdown(
        metric_card("Current Price", f"${current_price:,.2f}", f"6M move: {price_change:.2f}%"),
        unsafe_allow_html=True,
    )
    metric_cols[2].markdown(
        metric_card("Sentiment Score", f"{overall_sentiment:.2f} / 1.00", f"{state.get('bullish_count', 0)} bullish · {state.get('bearish_count', 0)} bearish"),
        unsafe_allow_html=True,
    )
    metric_cols[3].markdown(
        metric_card("Risk Read", f"{metrics.get('volatility', 0.0):.2f}%", f"RSI {metrics.get('rsi', 0.0):.2f}"),
        unsafe_allow_html=True,
    )

    report_tab, charts_tab, news_tab = st.tabs(["Research Report", "Market Charts", "News Desk"])

    with report_tab:
        report_col, summary_col = st.columns([1.45, 1.0])
        with report_col:
            st.markdown('<div class="section-label">AI Research Report</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="panel-card body-copy">{format_report_html(state.get("final_report", "No report generated."))}</div>',
                unsafe_allow_html=True,
            )
        with summary_col:
            st.markdown('<div class="section-label">Technical Pattern Summary</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="panel-card body-copy">{format_copy_html(state.get("pattern_summary", "No pattern summary generated."))}</div>',
                unsafe_allow_html=True,
            )
            render_sentiment_breakdown(sentiment_results)

    with charts_tab:
        if stock_df is not None and not stock_df.empty:
            chart_col, volume_col = st.columns(2)
            with chart_col:
                st.markdown('<div class="section-label">Price Structure</div>', unsafe_allow_html=True)
                st.plotly_chart(create_price_chart(stock_df), use_container_width=True)
            with volume_col:
                st.markdown('<div class="section-label">Liquidity Pulse</div>', unsafe_allow_html=True)
                st.plotly_chart(create_volume_chart(stock_df), use_container_width=True)
        else:
            st.info("Historical market data is unavailable for this ticker.")

    with news_tab:
        news_col, detail_col = st.columns([1.2, 1.0])
        with news_col:
            render_news(raw_news)
        with detail_col:
            st.markdown('<div class="section-label">Sentiment Detail</div>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="panel-card">
                    <div class="recommendation-chip">Overall Signal · {sentiment_label}</div>
                    <div class="body-copy">
                        Average headline score is <strong>{overall_sentiment:.2f}</strong> on a
                        bearish-to-bullish scale, with <strong>{state.get('neutral_count', 0)}</strong>
                        neutral headlines in the current batch.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_sentiment_breakdown(sentiment_results)
