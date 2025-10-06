from __future__ import annotations

from fastapi import Request

from app.utils.problem_details import ProblemDetailsException


def extract_owner_key(request: Request) -> str:
    authorization = request.headers.get("authorization")
    if not authorization:
        raise ProblemDetailsException(
            status_code=401,
            title="Unauthorized",
            detail="인증 토큰이 필요합니다.",
            type_suffix="unauthorized",
        )

    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise ProblemDetailsException(
            status_code=401,
            title="Unauthorized",
            detail="Authorization 헤더 형식이 올바르지 않습니다.",
            type_suffix="unauthorized",
        )

    token = parts[1].strip()
    if not token:
        raise ProblemDetailsException(
            status_code=401,
            title="Unauthorized",
            detail="인증 토큰이 필요합니다.",
            type_suffix="unauthorized",
        )

    return token
