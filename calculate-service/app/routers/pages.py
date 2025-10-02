from fastapi import APIRouter, Query, Request
from dataclasses import asdict

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..category_service import (
    build_category_cards,
    resolve_allowed_categories,
    resolve_primary_category,
)
from ..problem_bank import get_problems


def get_router(templates: Jinja2Templates) -> APIRouter:
    router = APIRouter(tags=["pages"])

    @router.get("/", response_class=HTMLResponse)
    async def home(request: Request) -> HTMLResponse:
        categories = resolve_allowed_categories()
        cards = build_category_cards(categories)
        primary_category = resolve_primary_category(categories)
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "categories": categories,
                "category_cards": cards,
                "primary_category": primary_category,
                "category_count": len(cards),
            },
        )

    @router.get("/problems", response_class=HTMLResponse)
    async def problems(
        request: Request,
        category: str = Query(default=None, description="문제 유형"),
    ) -> HTMLResponse:
        categories = resolve_allowed_categories()
        selected_category = category if category in categories else resolve_primary_category(categories)
        if not selected_category:
            problems_payload: list[dict[str, object]] = []
        else:
            problems_payload = [asdict(problem) for problem in get_problems(selected_category)]
        return templates.TemplateResponse(
            "problems.html",
            {
                "request": request,
                "category": selected_category,
                "category_display": (selected_category or "문제"),
                "problems": problems_payload,
                "categories": categories,
                "primary_category": resolve_primary_category(categories),
            },
        )

    return router


__all__ = ["get_router"]
