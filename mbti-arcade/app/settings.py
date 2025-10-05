from __future__ import annotations

import os
from urllib.parse import urlparse


_DEFAULT_ALLOWED_HOSTS = (
    "localhost",
    "127.0.0.1",
    "localhost:8000",
    "127.0.0.1:8000",
    "0.0.0.0",
    "0.0.0.0:8000",
    "testserver",
)


def _clean_hosts(raw_hosts: str) -> list[str]:
    hosts: list[str] = []
    for chunk in raw_hosts.split(","):
        candidate = chunk.strip()
        if not candidate:
            continue
        if candidate == "*":
            return ["*"]
        if candidate not in hosts:
            hosts.append(candidate)
    return hosts


CANONICAL_BASE_URL = os.getenv("CANONICAL_BASE_URL", "").strip()


def _resolve_calculate_service_base_url() -> str:
    """Return the public base URL for the standalone calculate service."""

    declared_urls = (
        os.getenv("CALCULATE_SERVICE_URL", "").strip(),
        os.getenv("CALCULATE_SERVICE_BASE_URL", "").strip(),
    )

    for candidate in declared_urls:
        if candidate:
            normalized = candidate.rstrip("/")
            return normalized or "/"

    return "https://calc.360me.app"


def _load_allowed_hosts() -> list[str]:
    declared = _clean_hosts(os.getenv("ALLOWED_HOSTS", ""))

    if declared == ["*"]:
        return declared

    if CANONICAL_BASE_URL:
        parsed = urlparse(CANONICAL_BASE_URL)
        netloc = (parsed.netloc or parsed.path).strip()
        if netloc and netloc not in declared:
            declared.append(netloc)

    for fallback in _DEFAULT_ALLOWED_HOSTS:
        if fallback not in declared:
            declared.append(fallback)

    return declared or list(_DEFAULT_ALLOWED_HOSTS)


ALLOWED_HOSTS = _load_allowed_hosts()


CALCULATE_SERVICE_BASE_URL = _resolve_calculate_service_base_url()

