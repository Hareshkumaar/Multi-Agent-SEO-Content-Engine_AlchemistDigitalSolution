from concurrent.futures import ThreadPoolExecutor

from fastapi import HTTPException

from app.db.repositories.agent_runs import agent_runs
from app.db.repositories.articles import articles


def article_or_404(id: int) -> dict:
    row = articles.get(id)
    if not row:
        raise HTTPException(404, "Article not found")
    return row


def article_full(id: int) -> dict:
    """Fetch article and its agent_runs in parallel. Shared by the API and the review page."""
    with ThreadPoolExecutor(max_workers=2) as pool:
        art_f = pool.submit(articles.get, id)
        runs_f = pool.submit(agent_runs.select, article_id=id, order="id", desc=False)
        row = art_f.result()
        if not row:
            raise HTTPException(404, "Article not found")
        return {**row, "agent_runs": runs_f.result()}
