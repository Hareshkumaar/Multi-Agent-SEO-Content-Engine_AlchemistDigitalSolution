"""Export an article as clean Markdown, HTML (meta tags + FAQ schema) or JSON."""
import html
import json
import re


def faq_pairs(md: str) -> list[tuple[str, str]]:
    parts = re.split(r"(?im)^##\s*(?:faqs?|frequently asked).*$", md or "")
    if len(parts) < 2:
        return []
    items = re.split(r"(?m)^###\s+", parts[1])[1:]
    return [(q.strip(), a.strip()) for q, _, a in (i.partition("\n") for i in items)]


def _md(a: dict) -> str:
    return a["content_markdown"] or ""


def _json(a: dict) -> str:
    outline = a.get("outline_json") or {}
    keys = ("topic", "target_keyword", "search_intent", "meta_title", "meta_description",
            "content_markdown", "bilingual_summary", "quality_score", "status")
    data = {k: a.get(k) for k in keys[:5]} | {"outline": outline, "faqs": outline.get("faqs", [])} \
        | {k: a.get(k) for k in keys[5:]}
    return json.dumps(data, indent=2, ensure_ascii=False)


def _html(a: dict) -> str:
    import markdown

    schema = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": ans}}
                             for q, ans in faq_pairs(a["content_markdown"])]}
    ld = json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")
    esc = lambda v: html.escape(v or "", quote=True)  # noqa: E731
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<title>{esc(a["meta_title"])}</title>'
            f'<meta name="description" content="{esc(a["meta_description"])}">'
            f'<script type="application/ld+json">{ld}</script></head>'
            f'<body><article>{markdown.markdown(_md(a), extensions=["extra"])}</article></body></html>')


EXPORTERS = {"md": (_md, "text/markdown"), "html": (_html, "text/html"), "json": (_json, "application/json")}


def build_export(a: dict, fmt: str) -> tuple[str, str, str]:
    """Returns (body, media_type, filename)."""
    fn, media = EXPORTERS[fmt]
    slug = re.sub(r"[^a-z0-9]+", "-", a["topic"].lower()).strip("-")[:60] or "article"
    return fn(a), media, f"{slug}.{fmt}"
