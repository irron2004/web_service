"""Service layer for the couple perception-gap workflow."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from hashlib import sha256
from typing import Dict, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core_scoring import (
    DeltaBundle,
    build_insights,
    compute_deltas,
    compute_scale_means,
    flag_rules,
    rank_top_delta_items,
    summarize_gap,
)
from app.couple.constants import QUESTION_REGISTRY
from app.couple.models import (
    AuditEvent,
    CoupleParticipant,
    CoupleResponse,
    CoupleResult,
    CoupleSession,
    DecisionPacket,
)
from app.couple.schemas import (
    CoupleResultEnvelope,
    CoupleSessionCreate,
    CoupleSessionEnvelope,
    DecisionPacketDescriptor,
    KState,
    ParticipantEnvelope,
    ResponseUpsertRequest,
    ResponseUpsertResponse,
    SavedResponses,
    StageOneSnapshot,
)
from app.utils.problem_details import ProblemDetailsException


QUESTION_CODES = set(QUESTION_REGISTRY.keys())


def _ensure_question_codes(answers: Dict[str, int]) -> None:
    unknown = sorted(set(answers) - QUESTION_CODES)
    if unknown:
        raise ProblemDetailsException(
            status_code=400,
            title="Unknown Question",
            detail="알 수 없는 문항 코드가 포함되어 있습니다.",
            type_suffix="question-invalid",
            errors={"codes": unknown},
        )


def _resolve_code_ref() -> str:
    return (
        os.getenv("GIT_SHA")
        or os.getenv("CODE_REF")
        or os.getenv("COMMIT_SHA")
        or "unknown"
    )


class CoupleService:
    """Encapsulates persistence and scoring for the couple flow."""

    def __init__(self, db: Session, request_id: str | None = None) -> None:
        self.db = db
        self.request_id = request_id
        self.code_ref = _resolve_code_ref()

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------
    def create_session(self, payload: CoupleSessionCreate) -> CoupleSessionEnvelope:
        session = CoupleSession(k_threshold=payload.k_threshold)

        if payload.stage1_snapshot:
            session.k_value = payload.stage1_snapshot.k
            session.k_visible = (
                payload.stage1_snapshot.visible
                and payload.stage1_snapshot.k >= session.k_threshold
            )
            session.stage1_snapshot = payload.stage1_snapshot.model_dump()

        self.db.add(session)
        self.db.flush()

        requested = {item.role: item for item in payload.participants}
        for role in ("A", "B"):
            data = requested.get(role)
            participant = CoupleParticipant(
                session_id=session.id,
                role=role,
                nickname=data.nickname if data else None,
                email=data.email if data else None,
            )
            self.db.add(participant)

        self.db.flush()
        self._log_event(
            session,
            event_type="session.created",
            payload={
                "k_threshold": session.k_threshold,
                "k_value": session.k_value,
                "participants": [p.role for p in session.participants],
            },
        )

        envelope = self._session_to_envelope(session)
        return envelope

    def update_stage_one(self, session_id: str, snapshot: StageOneSnapshot) -> CoupleSessionEnvelope:
        session = self._get_session(session_id)
        session.k_value = snapshot.k
        session.k_visible = snapshot.visible and snapshot.k >= session.k_threshold
        if snapshot.k >= session.k_threshold and snapshot.visible:
            session.stage = max(session.stage, 2)
        session.stage1_snapshot = snapshot.model_dump()
        self.db.flush()
        self._log_event(
            session,
            event_type="stage1.updated",
            payload=session.stage1_snapshot,
        )
        return self._session_to_envelope(session)

    def get_session_envelope(self, session_id: str) -> CoupleSessionEnvelope:
        session = self._get_session(session_id)
        return self._session_to_envelope(session)

    # ------------------------------------------------------------------
    # Responses
    # ------------------------------------------------------------------
    def upsert_responses(
        self, session_id: str, request: ResponseUpsertRequest
    ) -> ResponseUpsertResponse:
        session = self._get_session(session_id)
        participant = self._get_participant(session, request.access_token)

        if request.stage < session.stage:
            raise ProblemDetailsException(
                status_code=409,
                title="Invalid Stage",
                detail="해당 단계는 이미 완료되었습니다.",
                type_suffix="stage-invalid",
            )

        self_answers = self._answers_to_dict(request.self_answers)
        guess_answers = self._answers_to_dict(request.guess_answers)

        _ensure_question_codes(self_answers)
        _ensure_question_codes(guess_answers)

        if request.stage > session.stage:
            allowed = min(session.stage + 1, 3)
            if request.stage > allowed:
                raise ProblemDetailsException(
                    status_code=409,
                    title="Stage Order Violation",
                    detail="단계를 건너뛸 수 없습니다.",
                    type_suffix="stage-order",
                )
            if request.stage == 3 and not self._can_progress(participant.role, session):
                raise ProblemDetailsException(
                    status_code=409,
                    title="Stage Order Violation",
                    detail="현재 단계가 완료되지 않았습니다.",
                    type_suffix="stage-order",
                )

        # Clear existing entries for idempotency.
        self.db.query(CoupleResponse).filter(
            CoupleResponse.session_id == session.id,
            CoupleResponse.participant_id == participant.id,
            CoupleResponse.kind == "self",
        ).delete(synchronize_session=False)
        self.db.query(CoupleResponse).filter(
            CoupleResponse.session_id == session.id,
            CoupleResponse.participant_id == participant.id,
            CoupleResponse.kind == "guess",
        ).delete(synchronize_session=False)

        for code, value in self_answers.items():
            self.db.add(
                CoupleResponse(
                    session_id=session.id,
                    participant_id=participant.id,
                    question_code=code,
                    kind="self",
                    value=value,
                    stage=request.stage,
                )
            )
        for code, value in guess_answers.items():
            self.db.add(
                CoupleResponse(
                    session_id=session.id,
                    participant_id=participant.id,
                    question_code=code,
                    kind="guess",
                    value=value,
                    stage=request.stage,
                )
            )

        self._mark_completion(session, participant.role, self_answers, guess_answers)
        self.db.flush()

        self._log_event(
            session,
            event_type="responses.upserted",
            payload={
                "role": participant.role,
                "stage": request.stage,
                "self_completed": session.a_self_completed if participant.role == "A" else session.b_self_completed,
                "guess_completed": session.a_guess_completed if participant.role == "A" else session.b_guess_completed,
                "k_value": session.k_value,
                "k_visible": session.k_visible,
            },
        )

        return ResponseUpsertResponse(
            session_id=session.id,
            role=participant.role,
            stage=request.stage,
            self_completed=self._is_complete(self_answers),
            guess_completed=self._is_complete(guess_answers),
            stage_progress={
                "a_self_completed": session.a_self_completed,
                "a_guess_completed": session.a_guess_completed,
                "b_self_completed": session.b_self_completed,
                "b_guess_completed": session.b_guess_completed,
            },
        )

    def fetch_responses(self, session_id: str, access_token: str) -> SavedResponses:
        session, participant = self._resolve_participant(session_id, access_token)

        self_rows = self.db.scalars(
            select(CoupleResponse)
            .where(
                CoupleResponse.session_id == session.id,
                CoupleResponse.participant_id == participant.id,
                CoupleResponse.kind == "self",
            )
        ).all()
        guess_rows = self.db.scalars(
            select(CoupleResponse)
            .where(
                CoupleResponse.session_id == session.id,
                CoupleResponse.participant_id == participant.id,
                CoupleResponse.kind == "guess",
            )
        ).all()

        return SavedResponses(
            session_id=session.id,
            role=participant.role,
            self_answers={row.question_code: row.value for row in self_rows},
            guess_answers={row.question_code: row.value for row in guess_rows},
        )

    # ------------------------------------------------------------------
    # Result computation
    # ------------------------------------------------------------------
    def compute_result(self, session_id: str) -> CoupleResultEnvelope:
        session = self._get_session(session_id)
        if not (
            session.a_self_completed
            and session.a_guess_completed
            and session.b_self_completed
            and session.b_guess_completed
        ):
            raise ProblemDetailsException(
                status_code=409,
                title="Session Incomplete",
                detail="양측 SELF/GUESS 응답이 모두 완료되어야 합니다.",
                type_suffix="stage-incomplete",
            )

        responses = self.db.scalars(
            select(CoupleResponse).where(CoupleResponse.session_id == session.id)
        ).all()

        a_self: Dict[str, int] = {}
        a_guess: Dict[str, int] = {}
        b_self: Dict[str, int] = {}
        b_guess: Dict[str, int] = {}

        for row in responses:
            target = None
            if row.participant.role == "A" and row.kind == "self":
                target = a_self
            elif row.participant.role == "A" and row.kind == "guess":
                target = a_guess
            elif row.participant.role == "B" and row.kind == "self":
                target = b_self
            elif row.participant.role == "B" and row.kind == "guess":
                target = b_guess
            if target is not None:
                target[row.question_code] = row.value

        for mapping, label in (
            (a_self, "A.self"),
            (a_guess, "A.guess"),
            (b_self, "B.self"),
            (b_guess, "B.guess"),
        ):
            missing_codes = QUESTION_CODES - set(mapping)
            if missing_codes:
                raise ProblemDetailsException(
                    status_code=400,
                    title="Responses Missing",
                    detail=f"{label} 응답이 누락되었습니다.",
                    type_suffix="responses-missing",
                    errors={label: sorted(missing_codes)[:10]},
                )

        scales_a_self = compute_scale_means(a_self)
        scales_a_guess = compute_scale_means(a_guess)
        scales_b_self = compute_scale_means(b_self)
        scales_b_guess = compute_scale_means(b_guess)

        deltas: DeltaBundle = compute_deltas(a_self, a_guess, b_self, b_guess)
        top_items = rank_top_delta_items(deltas.delta_items_a, deltas.delta_items_b)

        combined_scales = {
            scale: (scales_a_self[scale] + scales_b_self[scale]) / 2
            for scale in scales_a_self
        }
        raw_self_combined = {
            code: min(a_self.get(code, 4), b_self.get(code, 4))
            for code in QUESTION_CODES
        }

        flags = flag_rules(combined_scales, raw_self_combined)
        insights = build_insights(deltas.delta_scales_a, deltas.delta_scales_b, flags)
        gap_summary = summarize_gap(deltas.delta_scales_a, deltas.delta_scales_b)

        # Persist result snapshot.
        result = session.result or CoupleResult(session_id=session.id)
        result.scales = {
            "A": {"self": scales_a_self, "guess": scales_a_guess},
            "B": {"self": scales_b_self, "guess": scales_b_guess},
        }
        result.deltas = {
            "items_a": deltas.delta_items_a,
            "items_b": deltas.delta_items_b,
            "scales_a": deltas.delta_scales_a,
            "scales_b": deltas.delta_scales_b,
        }
        result.flags = flags
        result.insights = insights
        result.top_delta_items = top_items
        result.gap_summary = gap_summary
        session.result = result

        session.stage = max(session.stage, 3)
        session.stage3_completed = True
        session.last_computed_at = datetime.now(timezone.utc)

        packet = self._store_decision_packet(
            session,
            a_self=a_self,
            a_guess=a_guess,
            b_self=b_self,
            b_guess=b_guess,
            result=result,
        )

        self._log_event(
            session,
            event_type="result.computed",
            payload={
                "top_delta_items": top_items,
                "gap_grade": gap_summary.get("grade"),
                "packet_sha256": packet.packet_sha256,
                "code_ref": packet.code_ref,
                "model_id": packet.model_id,
                "k_state": {
                    "threshold": session.k_threshold,
                    "current": session.k_value,
                    "visible": session.k_visible,
                },
            },
        )

        return self._result_to_envelope(session, result, packet)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_session(self, session_id: str) -> CoupleSession:
        session = self.db.get(CoupleSession, session_id)
        if session is None:
            raise ProblemDetailsException(
                status_code=404,
                title="Session Not Found",
                detail="세션 정보를 찾을 수 없습니다.",
                type_suffix="session-not-found",
            )
        return session

    def _get_participant(self, session: CoupleSession, access_token: str) -> CoupleParticipant:
        participant = self.db.scalar(
            select(CoupleParticipant)
            .where(
                CoupleParticipant.session_id == session.id,
                CoupleParticipant.access_token == access_token,
            )
        )
        if participant is None:
            raise ProblemDetailsException(
                status_code=403,
                title="Participant Not Found",
                detail="권한이 없거나 토큰이 잘못되었습니다.",
                type_suffix="participant-invalid",
            )
        return participant

    def _resolve_participant(
        self, session_id: str, access_token: str
    ) -> tuple[CoupleSession, CoupleParticipant]:
        session = self._get_session(session_id)
        participant = self._get_participant(session, access_token)
        return session, participant

    def _answers_to_dict(self, answers: Iterable) -> Dict[str, int]:
        seen: Dict[str, int] = {}
        for item in answers:
            if item.code in seen:
                raise ProblemDetailsException(
                    status_code=400,
                    title="Duplicate Answer",
                    detail="동일 문항에 대한 중복 응답이 감지되었습니다.",
                    type_suffix="duplicate-answer",
                    errors={"code": item.code},
                )
            seen[item.code] = item.value
        return seen

    def _is_complete(self, answers: Dict[str, int]) -> bool:
        return len(answers) == len(QUESTION_CODES)

    def _mark_completion(
        self,
        session: CoupleSession,
        role: str,
        self_answers: Dict[str, int],
        guess_answers: Dict[str, int],
    ) -> None:
        completed_self = self._is_complete(self_answers)
        completed_guess = self._is_complete(guess_answers)

        if role == "A":
            session.a_self_completed = completed_self
            session.a_guess_completed = completed_guess
        elif role == "B":
            session.b_self_completed = completed_self
            session.b_guess_completed = completed_guess
        else:
            raise ProblemDetailsException(
                status_code=400,
                title="Unknown Role",
                detail="알 수 없는 역할입니다.",
                type_suffix="role-invalid",
            )

        if (
            session.a_self_completed
            and session.a_guess_completed
            and session.b_self_completed
            and session.b_guess_completed
        ):
            session.stage = max(session.stage, 3)
        else:
            session.stage = max(session.stage, 2)

    def _can_progress(self, role: str, session: CoupleSession) -> bool:
        if role == "A":
            return session.a_self_completed and session.a_guess_completed
        if role == "B":
            return session.b_self_completed and session.b_guess_completed
        raise ProblemDetailsException(
            status_code=400,
            title="Unknown Role",
            detail="알 수 없는 역할입니다.",
            type_suffix="role-invalid",
        )

    def _log_event(self, session: CoupleSession, event_type: str, payload: dict | None) -> None:
        prev = self.db.scalar(
            select(AuditEvent)
            .where(AuditEvent.session_id == session.id)
            .order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
        )
        prev_hash = prev.hash if prev else None
        body = json.dumps(
            {
                "event_type": event_type,
                "payload": payload,
                "ts": datetime.now(timezone.utc).isoformat(),
            },
            sort_keys=True,
            default=str,
        )
        digest = sha256(((prev_hash or "") + body).encode("utf-8")).hexdigest()
        event = AuditEvent(
            session_id=session.id,
            req_id=self.request_id,
            actor=None,
            event_type=event_type,
            payload=payload,
            prev_hash=prev_hash,
            hash=digest,
            code_ref=self.code_ref,
        )
        self.db.add(event)

    def _store_decision_packet(
        self,
        session: CoupleSession,
        *,
        a_self: Dict[str, int],
        a_guess: Dict[str, int],
        b_self: Dict[str, int],
        b_guess: Dict[str, int],
        result: CoupleResult,
    ) -> DecisionPacket:
        payload = {
            "inputs": {
                "a_self": a_self,
                "a_guess": a_guess,
                "b_self": b_self,
                "b_guess": b_guess,
                "k_state": {
                    "threshold": session.k_threshold,
                    "current": session.k_value,
                    "visible": session.k_visible,
                },
                "stage1_snapshot": session.stage1_snapshot,
            },
            "outputs": {
                "scales": result.scales,
                "deltas": result.deltas,
                "flags": result.flags,
                "insights": result.insights,
                "top_delta_items": result.top_delta_items,
                "gap_summary": result.gap_summary,
            },
            "code_ref": self.code_ref,
            "model_id": "core_scoring.v1",
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        digest = sha256(canonical).hexdigest()

        packet = DecisionPacket(
            session_id=session.id,
            packet_sha256=digest,
            payload=payload,
            code_ref=self.code_ref,
            model_id="core_scoring.v1",
        )
        self.db.add(packet)
        self.db.flush()
        return packet

    def _session_to_envelope(self, session: CoupleSession) -> CoupleSessionEnvelope:
        return CoupleSessionEnvelope(
            session_id=session.id,
            stage=session.stage,
            participants=[
                ParticipantEnvelope(
                    role=participant.role,
                    nickname=participant.nickname,
                    email=participant.email,
                    access_token=participant.access_token,
                )
                for participant in sorted(session.participants, key=lambda p: p.role)
            ],
            a_self_completed=session.a_self_completed,
            a_guess_completed=session.a_guess_completed,
            b_self_completed=session.b_self_completed,
            b_guess_completed=session.b_guess_completed,
            stage3_completed=session.stage3_completed,
            k_state=KState(
                threshold=session.k_threshold,
                current=session.k_value,
                visible=session.k_visible,
            ),
            stage1_snapshot=session.stage1_snapshot,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    def _result_to_envelope(
        self,
        session: CoupleSession,
        result: CoupleResult,
        packet: DecisionPacket,
    ) -> CoupleResultEnvelope:
        descriptor = DecisionPacketDescriptor(
            packet_sha256=packet.packet_sha256,
            created_at=packet.created_at,
            code_ref=packet.code_ref,
            model_id=packet.model_id,
        )
        return CoupleResultEnvelope(
            session_id=session.id,
            scales=result.scales or {},
            deltas=result.deltas or {},
            flags=result.flags or [],
            insights=result.insights or [],
            top_delta_items=result.top_delta_items or [],
            gap_summary=result.gap_summary or {},
            k_state=KState(
                threshold=session.k_threshold,
                current=session.k_value,
                visible=session.k_visible,
            ),
            decision_packet=descriptor,
            generated_at=session.last_computed_at or datetime.now(timezone.utc),
        )
