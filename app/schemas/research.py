from typing import List, Literal

from pydantic import BaseModel, Field, field_validator

from app.core.constants import INTENTS


class Fact(BaseModel):
    statement: str
    source: Literal["reference_url", "general_knowledge"]


class ResearchBrief(BaseModel):
    search_intent: Literal[INTENTS]  # type: ignore[valid-type]
    intent_reason: str
    primary_keyword: str
    secondary_keywords: List[str] = Field(min_length=3, max_length=6)
    key_angles: List[str] = Field(min_length=4, max_length=6)
    facts: List[Fact] = Field(min_length=5)
    audience_notes: str

    @field_validator("search_intent", mode="before")
    @classmethod
    def _normalise(cls, v):
        """LLMs return 'informational' or 'Informational'. Accept both, store the canonical label."""
        return {i.lower(): i for i in INTENTS}.get(str(v).strip().lower(), v)
