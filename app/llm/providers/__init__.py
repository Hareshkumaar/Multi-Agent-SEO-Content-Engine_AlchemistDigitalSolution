"""Shared HTTP client and provider registry. Every provider exposes complete(system, user, settings) -> (text, tin, tout)."""
import httpx

from app.core.constants import HTTP_TIMEOUT

http_client = httpx.Client(timeout=HTTP_TIMEOUT)

from app.llm.providers import gemini, groq  # noqa: E402

PROVIDERS = {"groq": groq.complete, "gemini": gemini.complete}
