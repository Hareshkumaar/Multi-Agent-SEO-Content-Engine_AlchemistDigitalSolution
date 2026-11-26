from langgraph.graph import END

from app.core.constants import MAX_REVISIONS, PASS_SCORE, PIPELINE


def route_after_critic(state: dict) -> str:
    """Back to the writer once when the score is low, otherwise finish."""
    return "writer" if state["score"] < PASS_SCORE and state.get("revisions", 0) < MAX_REVISIONS else END


def next_node(node: str, state: dict) -> str:
    """Which step runs after `node`. Used to tell the UI what to highlight next."""
    if node == "critic":
        nxt = route_after_critic(state)
        return "done" if nxt == END else nxt
    return PIPELINE[PIPELINE.index(node) + 1]
