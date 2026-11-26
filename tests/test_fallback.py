from unittest.mock import patch

import httpx

from app.core.config import Settings
from app.llm.client import PROVIDERS, call_llm


def test_provider_fallback_on_429(monkeypatch):
    req = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    resp = httpx.Response(429, request=req, text="rate limited")

    def fail_groq(*_):
        raise httpx.HTTPStatusError("429", request=req, response=resp)

    monkeypatch.setitem(PROVIDERS, "groq", fail_groq)
    monkeypatch.setitem(PROVIDERS, "gemini", lambda *_: ("{}", 1, 2))
    settings = Settings(llm_provider="groq", groq_api_key="a", gemini_api_key="b")
    with patch("app.llm.client.get_settings", return_value=settings):
        res = call_llm("s", "u")
    assert res.text == "{}"
    assert res.output_tokens == 2
