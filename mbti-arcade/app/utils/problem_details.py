from __future__ import annotations

from http import HTTPStatus
from typing import Dict, List, Optional

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

PROBLEM_TYPE_BASE = "https://api.360me.app/errors"


class ProblemDetailsException(HTTPException):
    def __init__(
        self,
        status_code: int,
        title: str,
        detail: str,
        type_suffix: str = "generic",
        errors: Optional[Dict[str, List[str]]] = None,
        instance: Optional[str] = None,
    ) -> None:
        self.errors = errors
        self.type_suffix = type_suffix
        self.instance_value = instance
        super().__init__(status_code=status_code, detail=detail, headers=None)
        self.title = title


def _default_title(status: int) -> str:
    try:
        return HTTPStatus(status).phrase
    except ValueError:
        return "Error"


def _normalize_detail(detail: object, fallback: str) -> str:
    if isinstance(detail, str):
        return detail
    if detail is None:
        return fallback
    return str(detail)


def problem_response(
    request: Request,
    status: int,
    title: str,
    detail: str,
    type_suffix: str = "generic",
    errors: Optional[Dict[str, List[str]]] = None,
) -> JSONResponse:
    instance = request.url.path
    body = {
        "type": f"{PROBLEM_TYPE_BASE}/{type_suffix}",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance,
    }
    if errors:
        body["errors"] = errors
    return JSONResponse(status_code=status, content=body)


def from_exception(request: Request, exc: ProblemDetailsException) -> JSONResponse:
    instance = exc.instance_value or request.url.path
    body = {
        "type": f"{PROBLEM_TYPE_BASE}/{exc.type_suffix}",
        "title": exc.title,
        "status": exc.status_code,
        "detail": exc.detail,
        "instance": instance,
    }
    if exc.errors:
        body["errors"] = exc.errors
    return JSONResponse(status_code=exc.status_code, content=body)


def from_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    status = exc.status_code
    title = _default_title(status)
    detail = _normalize_detail(exc.detail, title)
    type_suffix = f"http-{status}"
    return problem_response(request, status, title, detail, type_suffix=type_suffix)


def _map_validation_errors(errors: List[dict]) -> Dict[str, List[str]]:
    mapped: Dict[str, List[str]] = {}
    for error in errors:
        loc = error.get("loc", [])
        path = ".".join(str(part) for part in loc if part not in {"body", "query", "path"})
        if not path:
            path = ".".join(str(part) for part in loc) or "non_field_errors"
        message = error.get("msg", "Invalid value")
        mapped.setdefault(path, []).append(message)
    return mapped


def from_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = _map_validation_errors(exc.errors())
    detail = "요청 본문을 검증할 수 없습니다. 입력 값을 확인해주세요."
    return problem_response(
        request,
        status=422,
        title="Validation Failed",
        detail=detail,
        type_suffix="validation",
        errors=errors,
    )


def internal_server_error(request: Request) -> JSONResponse:
    detail = "예상치 못한 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    return problem_response(
        request,
        status=500,
        title="Internal Server Error",
        detail=detail,
        type_suffix="internal",
    )
