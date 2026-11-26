from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import article_full, article_or_404
from app.core.constants import ALLOWED, LIST_COLS
from app.db.repositories.articles import articles
from app.schemas.api import ArticleUpdate, StatusUpdate

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("")
def list_articles(status: str | None = None):
    return articles.select(LIST_COLS, status=status)


@router.get("/{id}")
def get_article(id: int):
    return article_full(id)


@router.patch("/{id}/status")
def set_status(body: StatusUpdate, article: dict = Depends(article_or_404)):
    if body.status not in ALLOWED.get(article["status"], []):
        raise HTTPException(400, f"Cannot move from {article['status']} to {body.status}")
    return articles.update(article["id"], {"status": body.status})


@router.put("/{id}")
def save_edits(body: ArticleUpdate, article: dict = Depends(article_or_404)):
    return articles.update(article["id"], body.model_dump(exclude_none=True))
