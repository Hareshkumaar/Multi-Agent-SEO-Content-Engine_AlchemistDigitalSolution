from unittest.mock import MagicMock, patch

import groq
import httpx
from langchain_core.messages import AIMessage

from app.core.config import Settings
from app.llm.client import PROVIDERS, call_llm
from app.llm.providers import invoke_chat


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


def test_langchain_invoke_and_groq_rate_limit_fallback(monkeypatch):
    req = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    resp = httpx.Response(429, request=req, text="rate limited")

    def fail_groq(*_):
        raise groq.RateLimitError("429", response=resp, body=None)

    fake_llm = MagicMock()
    fake_llm.invoke.return_value = AIMessage(
        content='{"ok": true}',
        usage_metadata={"input_tokens": 11, "output_tokens": 22, "total_tokens": 33},
    )

    monkeypatch.setitem(PROVIDERS, "groq", fail_groq)
    monkeypatch.setitem(PROVIDERS, "gemini", lambda sys, usr, s: invoke_chat(fake_llm, sys, usr))
    settings = Settings(llm_provider="groq", groq_api_key="a", gemini_api_key="b")
    with patch("app.llm.client.get_settings", return_value=settings):
        res = call_llm("s", "u")
    assert res.text == '{"ok": true}'
    assert res.input_tokens == 11 and res.output_tokens == 22
