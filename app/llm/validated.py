"""call_validated: ask for JSON, validate with Pydantic, retry with the error message appended."""
import re

from pydantic import BaseModel, ValidationError

from app.core.constants import LLM_RETRIES
from app.llm.client import call_llm

RETRY_NOTE = "\n\nYour previous answer was invalid. Fix these errors and return corrected JSON only:\n{err}"


def _clean(text: str) -> str:
    return re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()


def call_validated(system: str, user: str, schema: type[BaseModel]) -> tuple[BaseModel, dict]:
    """Returns (validated model, usage). Usage sums tokens and latency over every attempt."""
    usage = {"input_tokens": 0, "output_tokens": 0, "latency_ms": 0}
    err = ""
    for _ in range(LLM_RETRIES + 1):
        r = call_llm(system, user + (RETRY_NOTE.format(err=err) if err else ""))
        usage["input_tokens"] += r.input_tokens
        usage["output_tokens"] += r.output_tokens
        usage["latency_ms"] += r.latency_ms
        try:
            return schema.model_validate_json(_clean(r.text)), usage
        except ValidationError as e:
            err = str(e)[:800]
    raise RuntimeError(f"{schema.__name__} failed after {LLM_RETRIES + 1} attempts: {err}")
