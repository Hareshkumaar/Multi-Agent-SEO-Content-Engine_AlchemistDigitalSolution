"""Runs the whole LangGraph pipeline with a fake LLM and fake database to prove the Critic loop."""
import json

from app.db.repositories.agent_runs import agent_runs
from app.db.repositories.articles import articles
from app.llm.client import LLMResult
from app.pipeline.graph import graph
from tests.test_core import BRIEF

OUTLINE = {"h1": "SEO Tips", "sections": [{"h2": f"s{i}"} for i in range(4)],
           "meta_title": "SEO Tips", "meta_description": "Learn seo tips.", "faqs": ["a?", "b?", "c?"]}


def fake_llm(system, user):
    if "Agent 1" in user: body = {**BRIEF}
    elif "Agent 2" in user: body = OUTLINE
    elif "Agent 3" in user: body = {"content_markdown": "# SEO Tips\n" + "seo tips " * 50, "bilingual_summary": "Mukhtasar."}
    else: body = {"keyword_placement": 60, "readability": 60, "factual_consistency": 60, "fluff": 60,
                  "feedback": [{"issue": "thin", "fix": "expand", "severity": "high"}]}
    return LLMResult(json.dumps(body), 10, 20, 5)


def test_critic_loop_runs_one_revision(monkeypatch):
    runs, saved = [], {}
    monkeypatch.setattr("app.llm.validated.call_llm", fake_llm)
    monkeypatch.setattr(agent_runs, "log", lambda aid, name, usage, fb=None: runs.append(name))
    monkeypatch.setattr(articles, "update", lambda i, f: saved.update(f))
    nodes = [next(iter(u)) for u in graph.stream(
        {"article_id": 1, "topic": "seo tips", "audience": "a", "tone": "t", "mode": "bilingual",
         "reference_urls": [], "revisions": 0}, stream_mode="updates")]
    assert nodes == ["researcher", "outliner", "writer", "critic", "writer", "critic"]
    assert runs == ["researcher", "outliner", "writer", "critic", "writer_revision", "critic_reaudit"]
    assert saved["quality_score"] <= 79 and saved["critic_report_json"]["hard_failures"] >= 1
