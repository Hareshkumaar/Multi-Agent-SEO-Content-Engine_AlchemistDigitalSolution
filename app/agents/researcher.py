from app.agents.base import BaseAgent
from app.schemas.research import ResearchBrief
from app.services.reference import fetch_text


class Researcher(BaseAgent):
    name = "researcher"
    schema = ResearchBrief

    def variables(self, s):
        return {**{k: s[k] for k in ("topic", "audience", "tone", "mode")},
                "reference_text": fetch_text(s.get("reference_urls", []))}

    def state_update(self, obj, s):
        return {"brief": obj.model_dump()}

    def db_update(self, obj, s):
        return {"target_keyword": obj.primary_keyword, "search_intent": obj.search_intent,
                "research_brief_json": obj.model_dump()}
