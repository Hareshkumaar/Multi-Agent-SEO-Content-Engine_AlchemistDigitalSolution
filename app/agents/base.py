"""BaseAgent runs every agent: build prompt, call LLM, validate, log the run, persist, return changed state.
A new agent is one small subclass: a name, a schema, a prompt file and three tiny hooks."""
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.db.repositories.agent_runs import agent_runs
from app.db.repositories.articles import articles
from app.llm.validated import call_validated

PROMPTS = Path(__file__).parent / "prompts"
SYSTEM = "You are one specialised agent inside a content pipeline. Output ONLY valid JSON."
PROMPT = ChatPromptTemplate.from_messages([("system", SYSTEM), ("human", "{body}")])


def render(template: str, **values) -> str:
    """Fill {{placeholders}}. Non-string values are dumped as JSON."""
    for key, v in values.items():
        template = template.replace("{{" + key + "}}", v if isinstance(v, str) else json.dumps(v, ensure_ascii=False))
    return template


class BaseAgent:
    name: str = ""
    rerun_name: str | None = None          # agent_runs label when running again after Critic feedback
    schema: type[BaseModel]

    # ---- hooks each agent overrides ----
    def variables(self, state: dict) -> dict:
        raise NotImplementedError

    def state_update(self, obj: BaseModel, state: dict) -> dict:
        return {}

    def db_update(self, obj: BaseModel, state: dict) -> dict:
        return {}

    def log_feedback(self, obj: BaseModel, state: dict) -> dict | None:
        return None

    # ---- shared behaviour ----
    def prompt(self, state: dict) -> str:
        text = (PROMPTS / f"{self.name}.md").read_text(encoding="utf-8")
        schema = json.dumps(self.schema.model_json_schema())
        return render(text, **self.variables(state)) + "\n\nReturn ONLY JSON matching this JSON schema:\n" + schema

    def run(self, state: dict) -> dict:
        sys_msg, user_msg = PROMPT.format_messages(body=self.prompt(state))
        obj, usage = call_validated(sys_msg.content, user_msg.content, self.schema)
        is_rerun = bool(state.get("feedback"))   # Critic feedback exists only after the first audit
        label = self.rerun_name if (is_rerun and self.rerun_name) else self.name
        fb, fields = self.log_feedback(obj, state), self.db_update(obj, state)
        if fields:
            with ThreadPoolExecutor(max_workers=2) as pool:
                f1 = pool.submit(agent_runs.log, state["article_id"], label, usage, fb)
                f2 = pool.submit(articles.update, state["article_id"], fields)
                f1.result()
                f2.result()
        else:
            agent_runs.log(state["article_id"], label, usage, fb)
        return self.state_update(obj, state)
