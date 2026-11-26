from typing import TypedDict


class State(TypedDict, total=False):
    article_id: int
    topic: str
    audience: str
    tone: str
    mode: str                 # 'english' or 'bilingual'
    reference_urls: list
    brief: dict               # ResearchBrief
    outline: dict             # Outline
    draft: str                # markdown article
    bilingual_summary: str
    code_checks: dict         # deterministic checks
    score: int
    feedback: dict            # CriticReport + code check feedback
    revisions: int            # completed revision passes (0 or 1)
