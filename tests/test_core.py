"""Quick checks: schemas, SEO checks, router, status transitions, page rendering."""
import pytest
from fastapi.testclient import TestClient
from langgraph.graph import END
from pydantic import ValidationError

from app.checks.scoring import final_score, hard_failures
from app.checks.seo import run_checks
from app.db.repositories.agent_runs import agent_runs
from app.db.repositories.articles import articles
from app.main import app
from app.pipeline.routing import route_after_critic
from app.schemas.critic import CriticReport
from app.schemas.outline import Outline
from app.schemas.research import ResearchBrief

client = TestClient(app)
BRIEF = dict(search_intent="informational", intent_reason="x", primary_keyword="seo tips",
             secondary_keywords=["a", "b", "c"], key_angles=["1", "2", "3", "4"],
             facts=[{"statement": "f", "source": "general_knowledge"}] * 5, audience_notes="n")


def test_schemas_enforce_limits():
    assert ResearchBrief(**BRIEF).search_intent == "Informational"          # label is normalised
    with pytest.raises(ValidationError):
        ResearchBrief(**{**BRIEF, "search_intent": "Navigational"})
    sections = [{"h2": "x"}] * 4
    with pytest.raises(ValidationError):
        Outline(h1="h", sections=sections, meta_title="t" * 61, meta_description="d", faqs=["q"] * 3)


def test_keyword_checks_and_cap():
    outline = {"meta_title": "short", "meta_description": "short"}
    c = run_checks("# SEO Tips\n" + "word " * 20, "seo tips", outline)
    assert c["kw_in_h1"] and c["kw_in_first_100"] and c["word_count"] < 1000
    fails = hard_failures(c)
    assert len(fails) == 1 and "words" in fails[0]["issue"]
    report = CriticReport(keyword_placement=95, readability=95, factual_consistency=95, fluff=95, feedback=[])
    assert final_score(report, fails) == 79 and final_score(report, []) == 95


def test_router():
    assert route_after_critic({"score": 70, "revisions": 0}) == "writer"
    assert route_after_critic({"score": 70, "revisions": 1}) == END
    assert route_after_critic({"score": 85, "revisions": 0}) == END


def test_status_transitions(monkeypatch):
    monkeypatch.setattr(articles, "get", lambda i: {"id": i, "status": "draft"})
    monkeypatch.setattr(articles, "update", lambda i, f: {"id": i, **f})
    assert client.patch("/api/articles/1/status", json={"status": "published"}).status_code == 400
    assert client.patch("/api/articles/1/status", json={"status": "approved"}).status_code == 200
    assert client.get("/api/articles/1/export?format=md").status_code == 400    # not approved yet


def test_pages_render(monkeypatch):
    monkeypatch.setattr(articles, "get", lambda i: {"id": i, "topic": "seo tips", "status": "approved", "mode": "bilingual",
                        "quality_score": 72, "content_markdown": "# SEO Tips\n\n## FAQ\n### Why?\nBecause.",
                        "meta_title": "t", "meta_description": "d", "outline_json": {"faqs": ["Why?"]}})
    monkeypatch.setattr(agent_runs, "select", lambda *a, **k: [{"agent_name": "writer_revision", "latency_ms": 4000,
                        "input_tokens": 10, "output_tokens": 20}])
    assert client.get("/").status_code == 200 and client.get("/dashboard").status_code == 200
    assert client.get("/health").json() == {"status": "ok"}
    page = client.get("/articles/1/review")
    assert page.status_code == 200 and "Below 80" in page.text
    edit = client.get("/articles/1/edit")
    assert edit.status_code == 200 and "SEO snapshot" in edit.text
    for fmt, marker in (("md", "# SEO Tips"), ("html", "FAQPage"), ("json", '"faqs"')):
        r = client.get(f"/api/articles/1/export?format={fmt}")
        assert r.status_code == 200 and marker in r.text
