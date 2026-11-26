from typing import List, Literal

from pydantic import BaseModel, Field


class FeedbackItem(BaseModel):
    issue: str
    fix: str
    severity: Literal["high", "medium", "low"]


class CriticReport(BaseModel):
    keyword_placement: int = Field(ge=0, le=100)
    readability: int = Field(ge=0, le=100)
    factual_consistency: int = Field(ge=0, le=100)
    fluff: int = Field(ge=0, le=100)  # 100 means zero fluff
    feedback: List[FeedbackItem]
