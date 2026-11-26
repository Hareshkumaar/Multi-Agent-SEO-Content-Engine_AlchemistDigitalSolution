from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import articles, export, generate, health
from app.web import routes as web

PUBLIC = Path(__file__).resolve().parent.parent / "public"

app = FastAPI(title="Lede Studio", description="Multi-agent editorial and SEO content engine")
for r in (generate, articles, export):
    app.include_router(r.router, prefix="/api")
app.include_router(health.router)
app.include_router(web.router)
# On Vercel, public/ is served by the CDN. Locally FastAPI serves the same URLs.
for folder in ("css", "js"):
    app.mount(f"/{folder}", StaticFiles(directory=PUBLIC / folder, check_dir=False), name=folder)
