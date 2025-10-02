from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends, Response
from fastapi.responses import Response as FastAPIResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Session as SessionModel
from app.services.aggregator import recalculate_aggregate
from app.services.scoring import ScoringError
from app.utils.problem_details import ProblemDetailsException
from app.utils.privacy import NOINDEX_VALUE, apply_noindex_headers
from app.og import render_share_card

router = APIRouter(prefix="/share", tags=["share"])


@router.get("/og/{invite_token}.png")
async def generate_share_og(invite_token: str, db: Session = Depends(get_db)) -> Response:
    session = (
        db.query(SessionModel)
        .filter(SessionModel.invite_token == invite_token)
        .first()
    )
    if session is None:
        raise ProblemDetailsException(
            status_code=404,
            title="Invite Not Found",
            detail="초대 정보를 찾을 수 없습니다.",
            type_suffix="invite-not-found",
        )

    try:
        aggregate = recalculate_aggregate(db, session)
    except ScoringError as exc:
        raise ProblemDetailsException(
            status_code=400,
            title="Scoring Failed",
            detail=str(exc),
            type_suffix="scoring-error",
        ) from exc

    image_bytes = render_share_card(session, aggregate)
    etag = hashlib.sha256(image_bytes).hexdigest()

    response = FastAPIResponse(content=image_bytes, media_type="image/png")
    response.headers["Cache-Control"] = "public, max-age=600"
    response.headers["ETag"] = etag
    apply_noindex_headers(response)
    response.headers["X-Robots-Tag"] = NOINDEX_VALUE
    return response
