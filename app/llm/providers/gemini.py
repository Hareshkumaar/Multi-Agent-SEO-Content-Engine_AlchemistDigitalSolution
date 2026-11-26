from functools import lru_cache

from app.core.config import Settings
from app.core.constants import HTTP_TIMEOUT, LLM_MAX_TOKENS
from app.llm.providers import invoke_chat


@lru_cache(maxsize=4)
def _chat_model(api_key: str, model: str):
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.4,
        max_output_tokens=LLM_MAX_TOKENS,
        timeout=HTTP_TIMEOUT,
        max_retries=0,
        response_mime_type="application/json",
    )


def complete(system: str, user: str, s: Settings) -> tuple[str, int, int]:
    return invoke_chat(_chat_model(s.gemini_api_key, s.gemini_model), system, user)
