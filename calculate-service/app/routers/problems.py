from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from pydantic import BaseModel, Field

from ..category_service import resolve_allowed_categories
from ..problem_bank import Problem, get_problems
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api", tags=["problems"])


@router.get("/categories", summary="사용 가능한 문제 카테고리 나열")
async def categories() -> dict[str, list[str]]:
    available = resolve_allowed_categories()
    return {"categories": available, "count": len(available)}


@router.get("/problems", summary="카테고리별 문제 반환")
async def problems(
    category: str | None = Query(
        default=None,
        description="요청할 문제 유형 (기본값: 첫 번째 카테고리)",
    ),
) -> dict[str, object]:
    categories = resolve_allowed_categories()
    selected_category = category or (categories[0] if categories else None)

    if not selected_category:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "type": "https://360me.app/problems/not-found",
                "title": "문제 데이터를 찾을 수 없습니다",
                "status": 404,
                "detail": "등록된 문제 카테고리가 없습니다.",
            },
        )

    if selected_category not in categories:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "type": "https://360me.app/problems/invalid-category",
                "title": "지원하지 않는 카테고리",
                "status": 404,
                "detail": f"요청한 카테고리 '{selected_category}'를 찾을 수 없습니다.",
                "instance": f"/api/problems?category={selected_category}",
                "available": categories,
            },
        )

    items = [problem.to_dict(include_answer=True) for problem in get_problems(selected_category)]
    return {
        "category": selected_category,
        "items": items,
        "total": len(items),
    }


@router.post(
    "/problems/{problem_id}/attempts",
    status_code=status.HTTP_201_CREATED,
    summary="문제 풀이 제출",
    response_model=ProblemAttemptResponse,
)
async def submit_attempt(
    problem_id: str,
    payload: ProblemAttemptRequest,
    problem_repository: ProblemRepository = Depends(_get_problem_repository),
    attempt_repository: AttemptRepository = Depends(_get_attempt_repository),
) -> ProblemAttemptResponse:
    try:
        problem = problem_repository.get_problem(problem_id)
    except ProblemDataError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "type": "https://360me.app/problems/not-found",
                "title": "문제를 찾을 수 없습니다",
                "status": status.HTTP_404_NOT_FOUND,
                "detail": f"요청한 문제 '{problem_id}'가 존재하지 않습니다.",
            },
        ) from None

    is_correct = int(payload.answer) == problem.answer
    record = attempt_repository.record_attempt(
        problem_id=problem.id,
        submitted_answer=payload.answer,
        is_correct=is_correct,
    )

    return ProblemAttemptResponse(
        attempt_id=record.id,
        problem_id=record.problem_id,
        category=problem.category,
        is_correct=record.is_correct,
        submitted_answer=record.submitted_answer,
        correct_answer=problem.answer,
        attempted_at=record.attempted_at,
    )


__all__ = ["router"]
