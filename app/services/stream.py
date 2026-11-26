"""Server-Sent Events helper that runs the graph and reports each finished step."""
import json

from app.core.constants import LABELS, PIPELINE

SSE_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"}


def sse(data: dict) -> str:
    return "data: " + json.dumps(data) + "\n\n"


def run_stream(init: dict):
    from app.pipeline.graph import graph
    from app.pipeline.routing import next_node

    aid, state = init["article_id"], dict(init)
    yield sse({"article_id": aid, "node": "start", "next": PIPELINE[0]})
    try:
        for update in graph.stream(init, stream_mode="updates"):
            node, changes = next(iter(update.items()))
            state.update(changes)
            yield sse({"article_id": aid, "node": node, "label": LABELS[node],
                       "next": next_node(node, state), "score": changes.get("score")})
    except Exception as e:  # surface any agent failure to the UI instead of a dead stream
        yield sse({"article_id": aid, "node": "error", "message": str(e)[:300]})
        return
    yield sse({"article_id": aid, "node": "done"})
