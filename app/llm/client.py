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


def _try(name: str, system: str, user: str, settings, attempts: int):
    """Call one provider. Waits as long as it asks on 429 or 5xx, up to `attempts` tries."""
    for attempt in range(attempts):
        try:
            return PROVIDERS[name](system, user, settings)
        except httpx.TimeoutException as e:
            raise LLMError(f"{name} timed out") from e
        except httpx.HTTPStatusError as e:
            code = e.response.status_code
            if code not in RETRY_STATUS or attempt == attempts - 1:
                raise LLMError(f"{name} error {code}: {e.response.text[:300]}") from e
            wait = float(e.response.headers.get("retry-after", HTTP_BACKOFF * 2**attempt))
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
