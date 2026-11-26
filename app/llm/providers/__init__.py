"""Shared HTTP client, LangChain invoke helper, and provider registry."""
import httpx

from app.core.constants import HTTP_TIMEOUT

http_client = httpx.Client(timeout=HTTP_TIMEOUT, limits=httpx.Limits(keepalive_expiry=2.0))


def invoke_chat(llm, system: str, user: str) -> tuple[str, int, int]:
    """Invoke a LangChain chat model and return (text, input_tokens, output_tokens)."""
    from langchain_core.messages import HumanMessage, SystemMessage

    msg = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    usage = msg.usage_metadata or {}
    content = msg.content
    text = content if isinstance(content, str) else "".join(
        p.get("text", "") if isinstance(p, dict) else str(p) for p in content
    )
    return text, usage.get("input_tokens", 0), usage.get("output_tokens", 0)


from app.llm.providers import gemini, groq  # noqa: E402

PROVIDERS = {"groq": groq.complete, "gemini": gemini.complete}
