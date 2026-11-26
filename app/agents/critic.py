from app.agents.base import BaseAgent
from app.checks.scoring import final_score, hard_failures
from app.checks.seo import run_checks
from app.schemas.critic import CriticReport


class Critic(BaseAgent):
    name = "critic"
    rerun_name = "critic_reaudit"
    schema = CriticReport

    def _checks(self, s):
        return run_checks(s["draft"], s["brief"]["primary_keyword"], s["outline"])

    def variables(self, s):
        return {"brief": s["brief"], "outline": s["outline"], "draft": s["draft"], "checks": self._checks(s)}

    def _report(self, obj, s):
        """LLM rubric + code checks. Failed hard checks become high severity feedback and cap the score."""
        checks = self._checks(s)
        fails = hard_failures(checks)
        report = obj.model_dump()
        report["feedback"] = fails + report["feedback"]
        report.update(score=final_score(obj, fails), code_checks=checks, hard_failures=len(fails))
        return report

    def state_update(self, obj, s):
        r = self._report(obj, s)
        return {"feedback": r, "score": r["score"], "code_checks": r["code_checks"]}

    def db_update(self, obj, s):
        r = self._report(obj, s)
        return {"quality_score": r["score"], "critic_report_json": r}

    def log_feedback(self, obj, s):
        return self._report(obj, s)
