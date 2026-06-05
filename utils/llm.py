from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI


load_dotenv()


def _get_openrouter_api_key() -> Optional[str]:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        return api_key

    try:
        import streamlit as st

        secret_value = st.secrets.get("OPENROUTER_API_KEY")
        if secret_value:
            return str(secret_value)
    except Exception:
        pass

    return None


def get_llm():
    """Initialize LangChain LLM with OpenRouter."""
    api_key = _get_openrouter_api_key()
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is not set. Add it to your local .env file or "
            "to Streamlit Secrets as OPENROUTER_API_KEY = \"your_key_here\"."
        )

    return ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        model="mistralai/mistral-7b-instruct",
        temperature=0.3,
    )


def run_chain(template: str, input_vars: dict) -> str:
    """
    Run a LangChain prompt + model sequence with a PromptTemplate.

    Args:
        template: prompt template string with {variables}
        input_vars: dict of variable values

    Returns:
        LLM response as string
    """
    llm = get_llm()
    prompt = PromptTemplate(
        input_variables=list(input_vars.keys()),
        template=template,
    )
    chain = prompt | llm
    response = chain.invoke(input_vars)
    content = getattr(response, "content", response)
    if isinstance(content, list):
        return "".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in content
        ).strip()
    return str(content).strip()
