from app.core.config import Settings
from app.core.constants import LLM_MAX_TOKENS, REASONING_EFFORT
from app.llm.providers import http_client

URL = "https://api.groq.com/openai/v1/chat/completions"


def complete(system: str, user: str, s: Settings) -> tuple[str, int, int]:
    r = http_client.post(
        URL,
        headers={"Authorization": f"Bearer {s.groq_api_key}"},
        json={
            "model": s.groq_model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_object"},
            "max_tokens": LLM_MAX_TOKENS,
            "temperature": 0.4,
            **({"reasoning_effort": REASONING_EFFORT} if "gpt-oss" in s.groq_model else {}),
        },
    )
    r.raise_for_status()
    d = r.json()
    return d["choices"][0]["message"]["content"], d["usage"]["prompt_tokens"], d["usage"]["completion_tokens"]
