# Stock Research Agent

An AI-powered stock research app built with LangChain, LangGraph, Streamlit, DuckDuckGo search, and yfinance.

## Features

- Fetches recent stock news for a company
- Runs headline-level sentiment analysis with an OpenRouter-backed LLM
- Calculates technical metrics from six months of market data
- Produces a concise research report with a directional recommendation
- Visualizes price, moving averages, volume, and sentiment

## Project Structure

```text
stock-research-agent/
├── app.py
├── graph.py
├── agents/
├── utils/
├── charts/
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set `OPENROUTER_API_KEY`.

For Streamlit Community Cloud, add this in the app's Secrets editor:

```toml
OPENROUTER_API_KEY = "your_openrouter_api_key_here"
```

## Run

Start the Streamlit app:

```bash
streamlit run app.py
```

## Test

```bash
pytest
```

## Notes

- News results depend on DuckDuckGo availability.
- Market data is pulled from Yahoo Finance via `yfinance`.
- The generated report is for education only and not investment advice.
