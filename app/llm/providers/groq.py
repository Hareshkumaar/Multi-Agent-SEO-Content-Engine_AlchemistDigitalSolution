from functools import lru_cache

from app.core.config import Settings
from app.core.constants import HTTP_TIMEOUT, LLM_MAX_TOKENS, REASONING_EFFORT
from app.llm.providers import http_client, invoke_chat


@lru_cache(maxsize=4)
def _chat_model(api_key: str, model: str):
    from langchain_groq import ChatGroq

    return ChatGroq(
        model=model,
        api_key=api_key,
        temperature=0.4,
        max_tokens=LLM_MAX_TOKENS,
        request_timeout=HTTP_TIMEOUT,
        max_retries=0,
        http_client=http_client,
        reasoning_effort=REASONING_EFFORT if "gpt-oss" in model else None,
        model_kwargs={"response_format": {"type": "json_object"}},
    )


def complete(system: str, user: str, s: Settings) -> tuple[str, int, int]:
    return invoke_chat(_chat_model(s.groq_api_key, s.groq_model), system, user)
