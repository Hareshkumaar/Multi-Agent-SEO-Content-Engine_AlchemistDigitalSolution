from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.api.deps import article_full, article_or_404
from app.core import constants as c

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
templates.env.globals.update({k: getattr(c, k) for k in (
    "PASS_SCORE", "TITLE_MAX", "DESC_MAX", "MIN_WORDS", "FIRST_WORDS", "LABELS", "PIPELINE", "MODES", "STATUSES",
    "ALLOWED", "ACTION_LABELS", "EXPORT_FORMATS", "EXPORTABLE", "RUBRIC")})


def page(template: str):
    def view(request: Request):
        return templates.TemplateResponse(request, template)
    return view


for path, tpl in {"/": "welcome.html", "/dashboard": "dashboard.html"}.items():
    router.add_api_route(path, page(tpl), methods=["GET"])


def article_ctx(id: int) -> dict:
    a = article_full(id)
    return {"a": a, "report": a.get("critic_report_json") or {}}


@router.get("/articles/{id}/review")
def review_page(request: Request, id: int):
    return templates.TemplateResponse(request, "review.html", article_ctx(id))


@router.get("/articles/{id}/edit")
def edit_page(request: Request, id: int):
    return templates.TemplateResponse(request, "editor.html", {"a": article_or_404(id)})
