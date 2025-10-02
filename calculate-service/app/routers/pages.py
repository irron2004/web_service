from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..config import get_settings
from ..problem_bank import ProblemRepository, list_categories, refresh_cache

def _get_repository(request: Request) -> ProblemRepository:
    repository = getattr(request.app.state, "problem_repository", None)
    if repository is None:
        repository = refresh_cache(force=True)
        request.app.state.problem_repository = repository
    return repository


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
