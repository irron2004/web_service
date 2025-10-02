from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

DEFAULT_EXPIRES_HOURS = 72
REQUEST_ID_HEADER = "X-Request-ID"


def generate_session_id() -> str:
    return str(uuid4())


def generate_invite_token() -> str:
    return uuid4().hex


def compute_expiry(hours: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=hours)
