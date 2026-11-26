from app.agents.base import BaseAgent
from app.core.constants import DESC_MAX, TITLE_MAX
from app.schemas.outline import Outline


class Outliner(BaseAgent):
    name = "outliner"
    schema = Outline

    def variables(self, s):
        return {"brief": s["brief"], "title_max": str(TITLE_MAX), "desc_max": str(DESC_MAX)}

    def state_update(self, obj, s):
        return {"outline": obj.model_dump()}

    def db_update(self, obj, s):
        return {"outline_json": obj.model_dump(), "meta_title": obj.meta_title,
                "meta_description": obj.meta_description}
