from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..config import get_settings
from ..problem_bank import (
    ProblemDataError,
    ProblemRepository,
    list_categories,
    refresh_cache,
)

def _get_repository(request: Request) -> ProblemRepository:
    repository = getattr(request.app.state, "problem_repository", None)
    if repository is None:
        repository = refresh_cache(force=True)
        request.app.state.problem_repository = repository
    return repository


def _resolve_allowed_categories() -> list[str]:
    settings = get_settings()
    allowed = settings.allowed_problem_categories or []
    try:
        available = list_categories()
    except ProblemDataError:
        available = []

    if allowed:
        if not available:
            return []
        filtered = [category for category in allowed if category in available]
        return filtered

    return available


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
        if not categories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="등록된 문제 카테고리가 없습니다.",
            )

        selected_category = category if category in categories else categories[0]
        repository = _get_repository(request)
        return templates.TemplateResponse(
            "problems.html",
            {
                "request": request,
                "category": selected_category,
                "problems": [
                    {
                        "id": problem.id,
                        "question": problem.question,
                        "hint": problem.hint,
                        "category": problem.category,
                    }
                    for problem in repository.get_problems(selected_category)
                ],
                "categories": categories,
            },
        )

    return router


__all__ = ["get_router"]
