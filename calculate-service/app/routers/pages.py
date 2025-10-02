from dataclasses import asdict

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..category_service import (
    build_category_cards,
    resolve_allowed_categories,
    resolve_primary_category,
)
from ..problem_bank import get_problems


router = APIRouter(tags=["pages"])


def _get_templates(request: Request) -> Jinja2Templates:
    templates = getattr(request.app.state, "templates", None)
    if not isinstance(templates, Jinja2Templates):
        raise RuntimeError("Templates are not configured on the application state.")
    return templates


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    templates = _get_templates(request)
    categories = resolve_allowed_categories()
    cards = build_category_cards(categories)
    primary_category = resolve_primary_category(categories)
    secondary_category = None
    if categories:
        for label in categories:
            if primary_category and label == primary_category:
                continue
            secondary_category = label
            break
        if secondary_category is None:
            secondary_category = primary_category
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "categories": categories,
            "category_cards": cards,
            "primary_category": primary_category,
            "secondary_category": secondary_category,
            "cta_primary_category": primary_category or (categories[0] if categories else None),
            "category_count": len(cards),
        },
    )


@router.get("/problems", response_class=HTMLResponse)
async def problems(
    request: Request,
    category: str = Query(default=None, description="문제 유형"),
) -> HTMLResponse:
    templates = _get_templates(request)
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
            "category_available": bool(selected_category),
        },
    )


__all__ = ["router"]
