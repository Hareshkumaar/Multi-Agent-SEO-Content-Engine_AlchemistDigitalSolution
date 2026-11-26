from threading import Lock
from typing import TYPE_CHECKING

from app.core.config import get_settings

if TYPE_CHECKING:
    from supabase import Client

_db: "Client | None" = None
_lock = Lock()


def get_db() -> "Client":
    """Service key stays on the server. The browser never talks to Supabase."""
    global _db
    if _db is None:
        with _lock:
            if _db is None:
                from supabase import create_client

                s = get_settings()
                _db = create_client(s.supabase_url, s.supabase_service_key)
    return _db
