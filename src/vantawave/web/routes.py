from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, PlainTextResponse


router = APIRouter(tags=["SOC Dashboard"])
WEB_ROOT = Path(__file__).resolve().parent


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return (WEB_ROOT / "index.html").read_text(encoding="utf-8")


@router.get("/dashboard/app.css", response_class=PlainTextResponse)
def dashboard_css():
    return PlainTextResponse(
        (WEB_ROOT / "app.css").read_text(encoding="utf-8"),
        media_type="text/css",
    )


@router.get("/dashboard/app.js", response_class=PlainTextResponse)
def dashboard_js():
    return PlainTextResponse(
        (WEB_ROOT / "app.js").read_text(encoding="utf-8"),
        media_type="application/javascript",
    )
