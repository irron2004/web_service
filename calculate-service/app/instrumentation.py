import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("calculate_service")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Ensure every request surfaces a request ID and basic timing for observability."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:  # type: ignore[override]
        start = time.perf_counter()
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex)
        request.state.request_id = request_id

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        # Prevent accidental indexing of result/problem pages.
        response.headers.setdefault("X-Robots-Tag", "noindex")
        response.headers.setdefault("Cache-Control", "no-store")

        logger.info(
            "request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )
        return response


def bind_request_id(request: Request) -> Callable[[logging.LogRecord], None]:
    """Helper to inject request_id into structured logs if needed."""

    def processor(record: logging.LogRecord) -> None:
        setattr(record, "request_id", getattr(request.state, "request_id", "unknown"))

    return processor


__all__ = ["RequestContextMiddleware", "bind_request_id"]
