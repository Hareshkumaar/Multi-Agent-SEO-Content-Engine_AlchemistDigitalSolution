from app.agents.base import BaseAgent
from app.core.constants import MIN_WORDS, TARGET_WORDS
from app.schemas.draft import Draft


class Writer(BaseAgent):
    name = "writer"
    rerun_name = "writer_revision"
    schema = Draft

    def variables(self, s):
        fb = s.get("feedback")
        revision = ("REVISION PASS. Previous draft:\n" + s["draft"] +
                    "\n\nFix ONLY these issues and keep everything else unchanged:\n" + str(fb["feedback"])) if fb else ""
        return {"brief": s["brief"], "outline": s["outline"], "audience": s["audience"], "tone": s["tone"],
                "bilingual": "yes" if s["mode"] == "bilingual" else "no",
                "target_words": str(TARGET_WORDS), "min_words": str(MIN_WORDS), "revision": revision}

    def _summary(self, obj, s):
        return obj.bilingual_summary if s["mode"] == "bilingual" else ""

    def state_update(self, obj, s):
        # revisions counts completed revision passes; the router reads it
        return {"draft": obj.content_markdown, "bilingual_summary": self._summary(obj, s),
                "revisions": s.get("revisions", 0) + (1 if s.get("feedback") else 0)}

    def db_update(self, obj, s):
        return {"content_markdown": obj.content_markdown, "bilingual_summary": self._summary(obj, s)}
