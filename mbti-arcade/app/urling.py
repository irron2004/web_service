from __future__ import annotations

import os
from functools import lru_cache

from fastapi import Request
from starlette.datastructures import URL

INVITE_ROUTE_NAME = "invite_public"
_LOCAL_HTTP_HOSTS = {"localhost", "127.0.0.1", "testserver"}


def _parse_canonical_base(raw: str | None) -> URL | None:
    if not raw:
        return None
    candidate = raw.strip()
    if not candidate:
        return None
    if "://" not in candidate:
        candidate = f"https://{candidate}"
    try:
        url = URL(candidate)
    except ValueError:
        return None
    if not url.scheme or not url.hostname:
        return None
    return url


@lru_cache(maxsize=1)
def _canonical_base() -> URL | None:
    return _parse_canonical_base(os.getenv("CANONICAL_BASE_URL"))


def build_invite_url(request: Request, token: str) -> str:
    target_url = URL(str(request.url_for(INVITE_ROUTE_NAME, token=token)))
    base = _canonical_base()
    if not base:
        if target_url.scheme != "https" and target_url.hostname not in _LOCAL_HTTP_HOSTS:
            target_url = target_url.replace(scheme="https")
        return str(target_url)

    base_path = base.path.rstrip("/") if base.path not in {"", "/"} else ""
    combined_path = f"{base_path}{target_url.path}" if base_path else target_url.path
    return str(
        base.replace(
            scheme=base.scheme,
            netloc=base.netloc,
            path=combined_path,
            query=target_url.query,
            fragment=target_url.fragment,
        )
    )

