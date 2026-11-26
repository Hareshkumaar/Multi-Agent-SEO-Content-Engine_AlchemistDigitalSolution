"""Fetch and trim text from optional reference URLs for the Researcher in parallel."""
from concurrent.futures import ThreadPoolExecutor
import re

import httpx

from app.core.constants import MAX_REF_URLS, REF_CHARS


def _fetch_one(client: httpx.Client, url: str) -> str:
    try:
        html = client.get(url).text
        text = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>|<[^>]+>", " ", html)
        return f"[{url}]\n{re.sub(r'\\s+', ' ', text)[:REF_CHARS]}"
    except httpx.HTTPError:
        return f"[{url}] could not be fetched."


def fetch_text(urls: list[str]) -> str:
    valid = [u for u in urls[:MAX_REF_URLS] if u.startswith(("http://", "https://"))]
    if not valid:
        return "None provided."
    with httpx.Client(timeout=15, follow_redirects=True) as client:
        with ThreadPoolExecutor(max_workers=len(valid)) as pool:
            return "\n\n".join(pool.map(lambda u: _fetch_one(client, u), valid))
