from __future__ import annotations

import os
import socket
import time
from datetime import datetime, timezone
from typing import Any, Dict
from urllib.parse import urlparse

from anyio import to_thread
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine

try:  # pragma: no cover - optional dependency
    from redis import asyncio as redis_asyncio  # type: ignore[import]
except ImportError:  # pragma: no cover - optional dependency
    redis_asyncio = None  # type: ignore[assignment]

router = APIRouter(tags=["system"])

_STARTED_AT = time.time()
_DEFAULT_REDIS_TIMEOUT = float(os.getenv("REDIS_HEALTH_TIMEOUT", "2.0"))


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/healthz")
async def healthz() -> Dict[str, Any]:
    """Liveness probe used by load balancers and uptime checks."""

    uptime = time.time() - _STARTED_AT
    return {
        "status": "ok",
        "service": os.getenv("SERVICE_NAME", "perception-gap-api"),
        "time": _utc_now(),
        "uptime_seconds": round(uptime, 3),
        "dependencies": ["database", "redis"],
    }


@router.get("/readyz")
async def readyz() -> JSONResponse:
    """Readiness probe that verifies downstream dependencies."""

    db_check = await _check_database()
    redis_check = await _check_redis()

    checks = {"database": db_check, "redis": redis_check}
    is_ready = all(check.get("status") == "ok" for check in checks.values())

    payload = {
        "status": "ready" if is_ready else "degraded",
        "time": _utc_now(),
        "checks": checks,
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=payload,
    )


async def _check_database() -> Dict[str, Any]:
    try:
        await to_thread.run_sync(_ping_database)
    except SQLAlchemyError as exc:  # pragma: no cover - defensive branch
        return {"status": "error", "detail": _truncate(str(exc))}
    except Exception as exc:  # pragma: no cover - defensive branch
        return {"status": "error", "detail": _truncate(str(exc))}

    return {
        "status": "ok",
        "dialect": engine.dialect.name,
        "driver": engine.url.drivername,
    }


def _ping_database() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


async def _check_redis() -> Dict[str, Any]:
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return {"status": "error", "detail": "REDIS_URL not configured"}

    try:
        await _ping_redis(redis_url)
    except Exception as exc:  # pragma: no cover - defensive branch
        return {"status": "error", "detail": _truncate(str(exc))}

    return {"status": "ok"}


async def _ping_redis(url: str) -> None:
    if redis_asyncio is not None:  # pragma: no branch - runtime decision
        client = redis_asyncio.Redis.from_url(
            url,
            encoding="utf-8",
            decode_responses=True,
        )
        try:
            await client.ping()
        finally:
            await client.close()
        return

    await to_thread.run_sync(_ping_redis_via_socket, url)


def _ping_redis_via_socket(url: str) -> None:
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or (6380 if parsed.scheme == "rediss" else 6379)
    if not host:
        raise ValueError("Redis URL missing hostname")

    with socket.create_connection((host, port), timeout=_DEFAULT_REDIS_TIMEOUT) as conn:
        conn.settimeout(_DEFAULT_REDIS_TIMEOUT)
        conn.sendall(b"*1\r\n$4\r\nPING\r\n")
        response = conn.recv(16)
        if not response.startswith(b"+PONG"):
            raise RuntimeError(f"Unexpected Redis response: {response!r}")


def _truncate(detail: str, limit: int = 200) -> str:
    if len(detail) <= limit:
        return detail
    return f"{detail[: limit - 3]}..."
