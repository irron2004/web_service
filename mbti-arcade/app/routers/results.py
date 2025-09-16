from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Session as SessionModel
from app.schemas import ResultDetail
from app.services.aggregator import recalculate_aggregate
from app.services.scoring import ScoringError
from app.utils.problem_details import ProblemDetailsException

router = APIRouter(prefix="/api", tags=["results"])


@router.get("/result/{invite_token}", response_model=ResultDetail)
async def fetch_result(invite_token: str, db: Session = Depends(get_db)):
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

    return ResultDetail(
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
