from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Optional

from app.services.aggregator import AggregateResult
from app.models import Session

from .image import Canvas

BACKGROUND = (15, 23, 42, 255)
CARD = (17, 99, 255, 255)
ACCENT = (18, 184, 166, 255)
TEXT_PRIMARY = (236, 252, 255, 255)
TEXT_SECONDARY = (148, 163, 184, 255)
LOCK_BG = (71, 85, 105, 255)
LOCK_TEXT = (226, 232, 240, 255)

log = logging.getLogger("perception_gap.og")


def _build_template() -> Canvas:
    template = Canvas(1200, 630, BACKGROUND)
    template.fill_rect(60, 90, 1080, 360, CARD)
    return template


_BASE_TEMPLATE = _build_template()


def render_share_card(session: Session, aggregate: AggregateResult) -> bytes:
    started = time.perf_counter()
    canvas = _BASE_TEMPLATE.clone()

    canvas.draw_text(80, 40, "360ME — PERCEPTION GAP", TEXT_SECONDARY, scale=3)
    canvas.draw_text(80, 120, f"SESSION: {session.id[:8]}", TEXT_PRIMARY, scale=4)

    timestamp = (
        session.updated_at or datetime.now(timezone.utc)
    ).strftime("%Y-%m-%d %H:%M")
    canvas.draw_text(80, 210, f"UPDATED: {timestamp}", TEXT_PRIMARY, scale=3)
    canvas.draw_text(80, 270, f"MODE: {session.mode.upper()}", TEXT_PRIMARY, scale=3)
    canvas.draw_text(80, 330, f"K: {aggregate.n}", TEXT_PRIMARY, scale=3)

    if aggregate.gap_score is not None:
        gap_str = f"GAP SCORE: {aggregate.gap_score:.1f}"
        canvas.draw_text(80, 390, gap_str, ACCENT, scale=4)
    else:
        canvas.fill_rect(80, 360, 1040, 120, LOCK_BG)
        canvas.draw_text(120, 400, "RESULTS LOCKED (K < 3)", LOCK_TEXT, scale=4)

    footer = "share safely at 360me"
    canvas.draw_text(80, 520, footer.upper(), TEXT_SECONDARY, scale=2)

    image = canvas.to_png()

    duration_ms = (time.perf_counter() - started) * 1000
    if duration_ms >= 150:
        log.warning(
            "OG card rendering slow",
            extra={
                "session_id": session.id,
                "duration_ms": round(duration_ms, 2),
                "mode": session.mode,
                "k": aggregate.n,
            },
        )
    else:
        log.debug(
            "OG card rendered",
            extra={
                "session_id": session.id,
                "duration_ms": round(duration_ms, 2),
            },
        )

    return image
