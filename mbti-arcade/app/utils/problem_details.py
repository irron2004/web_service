from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import HTTPException, Request
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
