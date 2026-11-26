from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.core.constants import DESC_MAX, MODES, STATUSES, TITLE_MAX


class GenerateRequest(BaseModel):
    topic: str = Field(min_length=5)
    audience: str = "General readers"
    tone: str = "clear, practical"
    mode: Literal[MODES] = "english"  # type: ignore[valid-type]
    reference_urls: list[str] = []


class StatusUpdate(BaseModel):
    status: Literal[STATUSES]  # type: ignore[valid-type]


class ArticleUpdate(BaseModel):
    content_markdown: Optional[str] = None
    bilingual_summary: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=TITLE_MAX)
    meta_description: Optional[str] = Field(None, max_length=DESC_MAX)
