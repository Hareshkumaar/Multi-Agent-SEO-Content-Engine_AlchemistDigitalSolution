"""The only place that talks to an LLM provider. Retries, falls back to the other provider, returns telemetry."""
import time
from dataclasses import dataclass

import httpx

from app.core.config import get_settings
from app.core.constants import HTTP_BACKOFF, HTTP_RETRIES, MAX_WAIT, RETRY_STATUS
from app.llm.providers import PROVIDERS


class LLMError(RuntimeError):
    pass


@dataclass
class LLMResult:
    text: str
    input_tokens: int
    output_tokens: int
    latency_ms: int


def _status_info(e: Exception) -> tuple[int, dict, str] | None:
    """Extract (status_code, headers, detail) from httpx, Groq, or Google GenAI HTTP errors."""
    resp = getattr(e, "response", None)
    code = getattr(e, "code", None) or getattr(e, "status_code", None) or (getattr(resp, "status_code", None) if resp is not None else None)
    if code is None:
        return None
    headers = getattr(resp, "headers", None) or {}
    text = getattr(resp, "text", None) or str(e)
    return int(code), headers, text[:300]


def _try(name: str, system: str, user: str, settings, attempts: int):
    """Call one provider. Waits as long as it asks on 429 or 5xx, up to `attempts` tries."""
    for attempt in range(attempts):
        try:
            return PROVIDERS[name](system, user, settings)
        except Exception as e:
            if isinstance(e, (httpx.TimeoutException, TimeoutError)) or type(e).__name__ == "APITimeoutError":
                raise LLMError(f"{name} timed out") from e
            if isinstance(e, httpx.TransportError) or type(e).__name__ == "APIConnectionError":
                if attempt == attempts - 1:
                    raise LLMError(f"{name} connection error: {str(e)[:200]}") from e
                time.sleep(min(HTTP_BACKOFF * 2**attempt, MAX_WAIT))
                continue
            info = _status_info(e)
            if not info:
                raise
            code, headers, detail = info
            if code not in RETRY_STATUS or attempt == attempts - 1:
                raise LLMError(f"{name} error {code}: {detail}") from e
            wait = float(headers.get("retry-after", HTTP_BACKOFF * 2**attempt))
            time.sleep(min(wait, MAX_WAIT))


def call_llm(system: str, user: str) -> LLMResult:
    s = get_settings()
    if s.llm_provider not in PROVIDERS:
        raise ValueError(f"LLM_PROVIDER must be one of {list(PROVIDERS)}")
    # chosen provider first, then any other provider that has a key
    names = [n for n in [s.llm_provider, *PROVIDERS] if getattr(s, f"{n}_api_key")]
    names = list(dict.fromkeys(names))
    if not names:
        raise ValueError("No LLM API key found in .env")
    start, errors = time.perf_counter(), []
    for i, name in enumerate(names):
        last = i == len(names) - 1
        try:
            text, tin, tout = _try(name, system, user, s, HTTP_RETRIES if last else 1)
            return LLMResult(text, tin, tout, int((time.perf_counter() - start) * 1000))
        except LLMError as e:
            errors.append(str(e))
    raise LLMError("; ".join(errors))
