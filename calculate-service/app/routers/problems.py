from fastapi import APIRouter, HTTPException, Query, status

from ..config import get_settings
from ..problem_bank import Problem, get_problems, list_categories

router = APIRouter(prefix="/api", tags=["problems"])


def _resolve_allowed_categories() -> list[str]:
    settings = get_settings()
    categories = settings.allowed_problem_categories or list_categories()
    return categories or list_categories()


@router.get("/categories", summary="사용 가능한 문제 카테고리 나열")
async def categories() -> dict[str, list[str]]:
    available = _resolve_allowed_categories()
    return {"categories": available, "count": len(available)}


@router.get("/problems", summary="카테고리별 문제 반환")
async def problems(
    category: str | None = Query(
        default=None,
        description="요청할 문제 유형 (기본값: 첫 번째 카테고리)",
    ),
) -> dict[str, object]:
    categories = _resolve_allowed_categories()
    selected_category = category or (categories[0] if categories else None)

    if not selected_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "type": "https://360me.app/problems/not-found",
                "title": "문제 데이터를 찾을 수 없습니다",
                "status": 404,
                "detail": "등록된 문제 카테고리가 없습니다.",
            },
        )

    if selected_category not in categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "type": "https://360me.app/problems/invalid-category",
                "title": "지원하지 않는 카테고리",
                "status": 404,
                "detail": f"요청한 카테고리 '{selected_category}'를 찾을 수 없습니다.",
                "instance": f"/api/problems?category={selected_category}",
                "available": categories,
            },
        )

    items = [problem.__dict__ for problem in get_problems(selected_category)]
    return {
        "category": selected_category,
        "items": items,
        "total": len(items),
    }


__all__ = ["router"]
