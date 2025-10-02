from __future__ import annotations

NOINDEX_VALUE = "noindex, nofollow"


def apply_noindex_headers(response) -> None:
    """Apply X-Robots-Tag headers to responses that must stay private."""
    response.headers["X-Robots-Tag"] = NOINDEX_VALUE
