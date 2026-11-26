from pydantic import BaseModel


class Draft(BaseModel):
    content_markdown: str
    bilingual_summary: str = ""
