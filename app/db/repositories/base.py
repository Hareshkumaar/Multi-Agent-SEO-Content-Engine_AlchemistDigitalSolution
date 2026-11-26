"""One generic repository. Each table gets a tiny subclass. Routes never write SQL."""
from app.db.client import get_db


class Repo:
    table = ""

    def insert(self, data: dict) -> dict:
        return get_db().table(self.table).insert(data).execute().data[0]

    def get(self, id: int) -> dict | None:
        rows = get_db().table(self.table).select("*").eq("id", id).limit(1).execute().data
        return rows[0] if rows else None

    def update(self, id: int, fields: dict) -> dict:
        return get_db().table(self.table).update(fields).eq("id", id).execute().data[0]

    def select(self, cols: str = "*", order: str = "created_at", desc: bool = True, **eq) -> list[dict]:
        q = get_db().table(self.table).select(cols)
        for key, value in eq.items():
            if value is not None:
                q = q.eq(key, value)
        return q.order(order, desc=desc).execute().data
