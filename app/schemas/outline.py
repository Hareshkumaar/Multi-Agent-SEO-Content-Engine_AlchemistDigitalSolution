from typing import List

from pydantic import BaseModel, Field

from app.core.constants import DESC_MAX, TITLE_MAX


class Section(BaseModel):
    h2: str
    h3s: List[str] = []


class Outline(BaseModel):
    h1: str
    sections: List[Section] = Field(min_length=4)
    meta_title: str = Field(max_length=TITLE_MAX)
    meta_description: str = Field(max_length=DESC_MAX)
    faqs: List[str] = Field(min_length=3, max_length=5)
