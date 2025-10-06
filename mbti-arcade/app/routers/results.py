from statistics import fmean

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Aggregate, Session as SessionModel
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


def _build_result_detail(
    session: SessionModel,
    aggregate_result,
    publish_other: bool,
) -> ResultDetail:
    return ResultDetail(
        session_id=session.id,
        mode=session.mode,
        n=aggregate_result.n,
        self_norm=aggregate_result.self_norm,
        other_norm=aggregate_result.other_norm if publish_other else None,
        gap=aggregate_result.gap if publish_other else None,
        sigma=aggregate_result.sigma if publish_other else None,
        gap_score=aggregate_result.gap_score if publish_other else None,
        radar_self=aggregate_result.radar_self,
        radar_other=aggregate_result.radar_other if publish_other else None,
        unlocked=publish_other,
    )


@router.get("/result/preview", response_model=ResultDetail)
async def preview_result(
    response: Response,
    db: Session = Depends(get_db),
) -> ResultDetail:
    session = (
        db.query(SessionModel)
        .join(Aggregate, Aggregate.session_id == SessionModel.id)
        .filter(Aggregate.n >= 3)
        .order_by(SessionModel.updated_at.desc())
        .first()
    )

    if session is None:
        return PREVIEW_RESULT

    try:
        aggregate_result = recalculate_aggregate(db, session)
    except ScoringError as exc:
        raise ProblemDetailsException(
            status_code=503,
            title="Preview Unavailable",
            detail="지금은 결과 미리보기를 제공할 수 없습니다. 잠시 후 다시 시도해 주세요.",
            type_suffix="preview-unavailable",
        ) from exc

    db.commit()

    publish_other = session.mode == "couple" or (aggregate_result.n or 0) >= 3

    result_payload = _build_result_detail(session, aggregate_result, publish_other)
    apply_noindex_headers(response)
    return result_payload


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
        aggregate_result = recalculate_aggregate(db, session)
    except ScoringError as exc:
        raise ProblemDetailsException(
            status_code=400,
            title="Scoring Failed",
            detail=str(exc),
            type_suffix="scoring-error",
        ) from exc

    db.commit()

    publish_other = session.mode == "couple" or (aggregate_result.n or 0) >= 3

    result_payload = _build_result_detail(session, aggregate_result, publish_other)

    apply_noindex_headers(response)

    return result_payload
