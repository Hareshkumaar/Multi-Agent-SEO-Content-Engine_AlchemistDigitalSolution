"""Deterministic checks. Python counts, the LLM never does."""
from app.core.constants import FIRST_WORDS


def run_checks(draft: str, keyword: str, outline: dict) -> dict:
    words = draft.split()
    kw = keyword.lower()
    first = " ".join(words[:FIRST_WORDS]).lower()
    h1 = next((line for line in draft.splitlines() if line.startswith("# ")), "").lower()
    return {
        "word_count": len(words),
        "kw_in_first_100": kw in first,
        "kw_in_h1": kw in h1,
        "kw_density": round(draft.lower().count(kw) / max(len(words), 1) * 100, 2),
        "meta_title_len": len(outline["meta_title"]),
        "meta_description_len": len(outline["meta_description"]),
    }
