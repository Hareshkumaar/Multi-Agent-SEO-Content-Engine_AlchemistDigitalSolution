from app.core.config import Settings
from app.core.constants import LLM_MAX_TOKENS
from app.llm.providers import http_client

URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def complete(system: str, user: str, s: Settings) -> tuple[str, int, int]:
    r = http_client.post(
        URL.format(model=s.gemini_model),
        headers={"x-goog-api-key": s.gemini_api_key},
        json={
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "maxOutputTokens": LLM_MAX_TOKENS,
                "temperature": 0.4,
            },
        },
    )
    r.raise_for_status()
    d = r.json()
    u = d.get("usageMetadata", {})
    text = "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"])
    return text, u.get("promptTokenCount", 0), u.get("candidatesTokenCount", 0)
