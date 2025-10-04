from __future__ import annotations

from fastapi import Request
from starlette.datastructures import URL

from app import settings

INVITE_ROUTE_NAME = "invite_public"


def canonicalize(url: URL) -> URL:
    canonical_base = settings.CANONICAL_BASE_URL
    if not canonical_base:
        return url

    try:
        base = URL(canonical_base)
    except ValueError:
        return url

    if not base.scheme or not base.netloc:
        return url

    path = url.path
    if base.path not in {"", "/"}:
        path = f"{base.path.rstrip('/')}{path}"

    return url.replace(scheme=base.scheme, netloc=base.netloc, path=path)


def build_invite_url(request: Request, token: str) -> str:
    invite_url = request.url_for(INVITE_ROUTE_NAME, token=token)
    return str(canonicalize(URL(str(invite_url))))

