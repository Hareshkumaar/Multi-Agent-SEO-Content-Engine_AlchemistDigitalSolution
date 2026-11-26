from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.db.repositories.articles import articles
from app.schemas.api import GenerateRequest
from app.services.stream import SSE_HEADERS, run_stream

router = APIRouter(tags=["generate"])


@router.post("/generate")
def generate(req: GenerateRequest):
    row = articles.insert({"topic": req.topic, "audience": req.audience, "tone": req.tone, "mode": req.mode})
    init = {**req.model_dump(), "article_id": row["id"], "revisions": 0}
    return StreamingResponse(run_stream(init), media_type="text/event-stream", headers=SSE_HEADERS)
