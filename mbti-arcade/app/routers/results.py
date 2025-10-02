from statistics import fmean

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Session as SessionModel
from app.schemas import ResultDetail
from app.services.aggregator import recalculate_aggregate
from app.services.scoring import ScoringError, norm_to_radar
from app.utils.problem_details import ProblemDetailsException
from app.utils.privacy import apply_noindex_headers

router = APIRouter(prefix="/api", tags=["results"])

PREVIEW_SELF_NORM = {'EI': 0.35, 'SN': -0.2, 'TF': 0.15, 'JP': -0.4}
PREVIEW_OTHER_NORM = {'EI': -0.1, 'SN': 0.4, 'TF': -0.05, 'JP': 0.2}
PREVIEW_GAP = {'EI': -0.45, 'SN': 0.6, 'TF': -0.2, 'JP': 0.6}
PREVIEW_SIGMA = {'EI': 0.32, 'SN': 0.27, 'TF': 0.41, 'JP': 0.38}
PREVIEW_GAP_SCORE = 46.25
PREVIEW_RESULT = ResultDetail(
    session_id="demo-session",
    mode="preview",
    n=4,
    self_norm=PREVIEW_SELF_NORM,
    other_norm=PREVIEW_OTHER_NORM,
    gap=PREVIEW_GAP,
    sigma=PREVIEW_SIGMA,
    gap_score=PREVIEW_GAP_SCORE,
    radar_self=norm_to_radar(PREVIEW_SELF_NORM),
    radar_other=norm_to_radar(PREVIEW_OTHER_NORM),
)


@router.get("/result/preview", response_model=ResultDetail)
async def preview_result() -> ResultDetail:
    return PREVIEW_RESULT


@router.get("/result/{invite_token}", response_model=ResultDetail)
async def fetch_result(
    invite_token: str,
    response: Response,
    db: Session = Depends(get_db),
):
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
        result = recalculate_aggregate(db, session)
    except ScoringError as exc:
        raise ProblemDetailsException(
            status_code=400,
            title="Scoring Failed",
            detail=str(exc),
            type_suffix="scoring-error",
        ) from exc

    db.commit()

    publish_other = True
    if session.mode != "couple" and (result.n or 0) < 3:
        publish_other = False

    result_payload = ResultDetail(
        session_id=session.id,
        mode=session.mode,
        n=result.n,
        self_norm=result.self_norm,
        other_norm=result.other_norm if publish_other else None,
        gap=result.gap if publish_other else None,
        sigma=result.sigma if publish_other else None,
        gap_score=result.gap_score if publish_other else None,
        radar_self=result.radar_self,
        radar_other=result.radar_other if publish_other else None,
    )

    apply_noindex_headers(response)

    return result_payload
