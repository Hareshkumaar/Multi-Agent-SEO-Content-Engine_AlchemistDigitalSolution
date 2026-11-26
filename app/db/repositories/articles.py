from datetime import datetime, timezone

from app.core.constants import T_ARTICLES
from app.db.repositories.base import Repo


class ArticlesRepo(Repo):
    table = T_ARTICLES

    def update(self, id: int, fields: dict) -> dict:
        return super().update(id, {**fields, "updated_at": datetime.now(timezone.utc).isoformat()})


articles = ArticlesRepo()
