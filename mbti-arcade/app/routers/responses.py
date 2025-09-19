import hashlib
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.data.loader import seed_questions
from app.data.questions import questions_for_mode
from app.database import get_db
from app.models import OtherResponse, Session as SessionModel, SelfResponse
from app.schemas import (
    AnswerItem,
    OtherSubmitRequest,
    OtherSubmitResponse,
    SelfSubmitRequest,
    SelfSubmitResponse,
)
from app.services.aggregator import recalculate_aggregate
from app.services.scoring import ScoringError
from app.utils.problem_details import ProblemDetailsException

router = APIRouter(prefix="/api", tags=["responses"])


def ensure_session_active(session: SessionModel) -> None:
    if session.expires_at < datetime.utcnow():
        raise ProblemDetailsException(
            status_code=410,
            title="Session Expired",
            detail="세션 초대 기한이 만료되었습니다.",
            type_suffix="session-expired",
        )


def validate_answers(mode: str, answers: list[AnswerItem]) -> None:
    question_payloads = questions_for_mode(mode)
    expected_ids = {item["id"] for item in question_payloads}
    provided_ids = [answer.question_id for answer in answers]

    messages: list[str] = []

    if len(provided_ids) != len(expected_ids):
        messages.append(
            f"문항 수가 일치하지 않습니다. 기대값={len(expected_ids)}, 입력값={len(provided_ids)}"
        )

    duplicates: list[int] = []
    seen: set[int] = set()
    for question_id in provided_ids:
        if question_id in seen:
            duplicates.append(question_id)
        else:
            seen.add(question_id)

    if duplicates:
        unique_dups = sorted(set(duplicates))
        messages.append(f"중복 문항 ID: {', '.join(map(str, unique_dups))}")

    unexpected = sorted(set(provided_ids) - expected_ids)
    if unexpected:
        messages.append(f"알 수 없는 문항 ID: {', '.join(map(str, unexpected))}")

    missing = sorted(expected_ids - set(provided_ids))
    if missing:
        messages.append(f"누락된 문항 ID: {', '.join(map(str, missing))}")

    if messages:
        raise ProblemDetailsException(
            status_code=400,
            title="Invalid Answers",
            detail="응답 문항 구성이 유효하지 않습니다.",
            type_suffix="answers-invalid",
            errors={"answers": messages},
        )


@router.post("/self/submit", response_model=SelfSubmitResponse)
async def submit_self(payload: SelfSubmitRequest, db: Session = Depends(get_db)):
    session = db.get(SessionModel, payload.session_id)
    if session is None:
        raise ProblemDetailsException(
            status_code=404,
            title="Session Not Found",
            detail="해당 세션을 찾을 수 없습니다.",
            type_suffix="session-not-found",
        )

    ensure_session_active(session)

    validate_answers(session.mode, payload.answers)

    seed_questions(db)

    try:
        db.query(SelfResponse).filter(SelfResponse.session_id == session.id).delete()

        for answer in payload.answers:
            db.add(
                SelfResponse(
                    session_id=session.id,
                    question_id=answer.question_id,
                    value=answer.value,
                )
            )

        db.flush()

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
    except ProblemDetailsException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

    return SelfSubmitResponse(
        session_id=session.id,
        self_norm=result.self_norm,
        self_radar=result.radar_self,
    )


def build_rater_hash(invite_token: str, payload: OtherSubmitRequest) -> str:
    base = payload.rater_key or "".join(
        f"{item.question_id}:{item.value};" for item in sorted(payload.answers, key=lambda x: x.question_id)
    )
    digest = hashlib.sha256(f"{invite_token}:{base}".encode("utf-8")).hexdigest()
    return digest


@router.post("/other/submit", response_model=OtherSubmitResponse, status_code=201)
async def submit_other(payload: OtherSubmitRequest, db: Session = Depends(get_db)):
    session = (
        db.query(SessionModel)
        .filter(SessionModel.invite_token == payload.invite_token)
        .first()
    )
    if session is None:
        raise ProblemDetailsException(
            status_code=404,
            title="Invite Not Found",
            detail="초대 정보를 찾을 수 없습니다.",
            type_suffix="invite-not-found",
        )

    ensure_session_active(session)

    validate_answers(session.mode, payload.answers)

    seed_questions(db)

    distinct_raters = (
        db.query(func.count(func.distinct(OtherResponse.rater_hash)))
        .filter(OtherResponse.session_id == session.id)
        .scalar()
        or 0
    )
    rater_hash = build_rater_hash(session.invite_token, payload)
    already_exists = (
        db.query(OtherResponse)
        .filter(
            OtherResponse.session_id == session.id,
            OtherResponse.rater_hash == rater_hash,
        )
        .first()
    )
    if distinct_raters >= session.max_raters and not already_exists:
        raise ProblemDetailsException(
            status_code=429,
            title="Capacity Reached",
            detail="해당 세션의 응답 한도를 초과했습니다.",
            type_suffix="rate-limit",
        )

    try:
        db.query(OtherResponse).filter(
            OtherResponse.session_id == session.id,
            OtherResponse.rater_hash == rater_hash,
        ).delete()

        for answer in payload.answers:
            db.add(
                OtherResponse(
                    session_id=session.id,
                    rater_hash=rater_hash,
                    question_id=answer.question_id,
                    value=answer.value,
                    relation_tag=payload.relation_tag,
                )
            )

        db.flush()

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
    except ProblemDetailsException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

    return OtherSubmitResponse(
        session_id=session.id,
        accepted=True,
        respondents=result.n,
    )
