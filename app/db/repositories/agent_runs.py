from app.core.constants import T_RUNS
from app.db.repositories.base import Repo


class AgentRunsRepo(Repo):
    table = T_RUNS

    def log(self, article_id: int, agent_name: str, usage: dict, feedback: dict | None = None) -> dict:
        return self.insert({"article_id": article_id, "agent_name": agent_name, **usage,
                            "critic_feedback_json": feedback})


agent_runs = AgentRunsRepo()
