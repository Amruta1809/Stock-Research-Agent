from __future__ import annotations

import plotly.graph_objects as go


def _x_axis(df):
    return df["Date"] if "Date" in df.columns else df.index


def _apply_chart_theme(figure: go.Figure, yaxis_title: str) -> go.Figure:
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10, 20, 33, 0.18)",
        margin=dict(l=10, r=10, t=12, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(color="#d7deea"),
        ),
        xaxis=dict(
            title="Date",
            showgrid=False,
            color="#c7d2e3",
            zeroline=False,
        ),
        yaxis=dict(
            title=yaxis_title,
            gridcolor="rgba(255,255,255,0.08)",
            color="#c7d2e3",
            zeroline=False,
        ),
        hoverlabel=dict(
            bgcolor="#102238",
            bordercolor="#27496d",
            font_color="#f4efe6",
        ),
    )
    return figure


def create_price_chart(df):
    chart_df = df.copy()
    chart_df["MA20"] = chart_df["Close"].rolling(20).mean()
    chart_df["MA50"] = chart_df["Close"].rolling(50).mean()
    x_axis = _x_axis(chart_df)

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=x_axis,
            y=chart_df["Close"],
            name="Close",
            line=dict(color="#7cc7ff", width=2.5),
        )
    )
    figure.add_trace(
        go.Scatter(
            x=x_axis,
            y=chart_df["MA20"],
            name="MA 20",
            line=dict(color="#0f8cff", width=2),
        )
    )
    figure.add_trace(
        go.Scatter(
            x=x_axis,
            y=chart_df["MA50"],
            name="MA 50",
            line=dict(color="#ffb3a7", width=2),
        )
    )
    return _apply_chart_theme(figure, "Price")


def create_volume_chart(df):
    x_axis = _x_axis(df)
    figure = go.Figure()
    figure.add_trace(
        go.Bar(
            x=x_axis,
            y=df["Volume"],
            name="Volume",
            marker_color="rgba(124, 199, 255, 0.86)",
        )
    )
    return _apply_chart_theme(figure, "Volume")


def create_sentiment_chart(bullish_count: int, bearish_count: int, neutral_count: int):
    figure = go.Figure(
        data=[
            go.Pie(
                labels=["Bullish", "Bearish", "Neutral"],
                values=[bullish_count, bearish_count, neutral_count],
                hole=0.45,
            )
        ]
    )
    figure.update_layout(title="News Sentiment Distribution")
    return figure
