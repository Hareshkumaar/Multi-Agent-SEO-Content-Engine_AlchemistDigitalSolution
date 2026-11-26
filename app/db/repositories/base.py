"""One generic repository. Each table gets a tiny subclass. Routes never write SQL."""
import httpx

from app.db.client import get_db, reset_db


def _exec(fn):
    try:
        return fn().execute()
    except httpx.TransportError:
        reset_db()
        return fn().execute()


class Repo:
    table = ""

    def insert(self, data: dict) -> dict:
        return _exec(lambda: get_db().table(self.table).insert(data)).data[0]

    def get(self, id: int) -> dict | None:
        rows = _exec(lambda: get_db().table(self.table).select("*").eq("id", id).limit(1)).data
        return rows[0] if rows else None

    def update(self, id: int, fields: dict) -> dict:
        return _exec(lambda: get_db().table(self.table).update(fields).eq("id", id)).data[0]

    def select(self, cols: str = "*", order: str = "created_at", desc: bool = True, **eq) -> list[dict]:
        def build():
            q = get_db().table(self.table).select(cols)
            for key, value in eq.items():
                if value is not None:
                    q = q.eq(key, value)
            return q.order(order, desc=desc)
        return _exec(build).data
