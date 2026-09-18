"""LLM provider factory: switch between OpenAI and Swisscom inference API.

Swisscom's inference API details (base URL, auth header, exact response
shape) are not finalized yet ("we add this later"). The Swisscom provider
below assumes an OpenAI-compatible chat completions endpoint reachable via
SWISSCOM_BASE_URL/SWISSCOM_API_KEY with model "aparthus" - adjust once the
real API contract is known.
"""

import os

from langchain_openai import ChatOpenAI


def get_llm(provider: str | None = None):
    """Return a LangChain chat model for the configured LLM provider."""
    provider = (provider or os.getenv("LLM_PROVIDER", "openai")).lower()

    if provider == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0,
        )

    if provider == "swisscom":
        base_url = os.getenv("SWISSCOM_BASE_URL")
        api_key = os.getenv("SWISSCOM_API_KEY")
        if not base_url or not api_key:
            raise RuntimeError(
                "SWISSCOM_BASE_URL and SWISSCOM_API_KEY must be set to use the swisscom provider."
            )
        return ChatOpenAI(
            model=os.getenv("SWISSCOM_MODEL", "aparthus"),
            api_key=api_key,
            base_url=base_url,
            temperature=0,
        )

    raise ValueError(f"Unknown LLM provider: {provider!r} (expected 'openai' or 'swisscom')")
