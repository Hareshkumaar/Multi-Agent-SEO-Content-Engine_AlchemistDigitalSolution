from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from app.api.deps import article_or_404
from app.core.constants import EXPORT_FORMATS, EXPORTABLE
from app.services.export import build_export

router = APIRouter(tags=["export"])


@router.get("/articles/{id}/export")
def export(format: Literal[EXPORT_FORMATS] = "md", article: dict = Depends(article_or_404)):  # type: ignore[valid-type]
    if article["status"] not in EXPORTABLE:
        raise HTTPException(400, "Approve the article before exporting it")
    body, media, name = build_export(article, format)
    return Response(body, media_type=media, headers={"Content-Disposition": f'attachment; filename="{name}"'})
