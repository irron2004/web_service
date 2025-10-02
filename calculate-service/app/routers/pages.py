from fastapi import APIRouter, Query, Request
from dataclasses import asdict

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..config import get_settings
from ..problem_bank import get_problems, list_categories


def _resolve_allowed_categories() -> list[str]:
    settings = get_settings()
    candidates = settings.allowed_problem_categories or list_categories()
    return candidates if candidates else list_categories()


def get_router(templates: Jinja2Templates) -> APIRouter:
    router = APIRouter(tags=["pages"])

    @router.get("/", response_class=HTMLResponse)
    async def home(request: Request) -> HTMLResponse:
        categories = _resolve_allowed_categories()
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "categories": categories,
            },
        )

    @router.get("/problems", response_class=HTMLResponse)
    async def problems(
        request: Request,
        category: str = Query(default=None, description="문제 유형"),
    ) -> HTMLResponse:
        categories = _resolve_allowed_categories()
        selected_category = category if category in categories else categories[0]
        return templates.TemplateResponse(
            "problems.html",
            {
                "request": request,
                "category": selected_category,
                "problems": [asdict(problem) for problem in get_problems(selected_category)],
                "categories": categories,
            },
        )

    return router


__all__ = ["get_router"]
