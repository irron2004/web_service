"""REST endpoints for the couple perception-gap flow."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.couple.schemas import (
    ComputeRequest,
    CoupleResultEnvelope,
    CoupleSessionCreate,
    CoupleSessionEnvelope,
    ResponseUpsertRequest,
    ResponseUpsertResponse,
    SavedResponses,
    StageOneSnapshot,
)
from app.couple.services import CoupleService
from app.database import get_db

router = APIRouter(prefix="/api/couples", tags=["couples"])


def get_couple_service(request: Request, db=Depends(get_db)) -> CoupleService:
    request_id = getattr(request.state, "request_id", None)
    return CoupleService(db, request_id=request_id)


@router.post("/sessions", response_model=CoupleSessionEnvelope, status_code=201)
async def create_session(
    payload: CoupleSessionCreate,
    service: CoupleService = Depends(get_couple_service),
) -> CoupleSessionEnvelope:
    try:
        envelope = service.create_session(payload)
        service.db.commit()
    except Exception:
        service.db.rollback()
        raise
    return envelope


@router.patch("/sessions/{session_id}/stage1", response_model=CoupleSessionEnvelope)
async def update_stage_one(
    session_id: str,
    payload: StageOneSnapshot,
    service: CoupleService = Depends(get_couple_service),
) -> CoupleSessionEnvelope:
    try:
        envelope = service.update_stage_one(session_id, payload)
        service.db.commit()
    except Exception:
        service.db.rollback()
        raise
    return envelope


@router.get("/sessions/{session_id}", response_model=CoupleSessionEnvelope)
async def fetch_session(
    session_id: str,
    service: CoupleService = Depends(get_couple_service),
) -> CoupleSessionEnvelope:
    return service.get_session_envelope(session_id)


@router.put(
    "/sessions/{session_id}/responses",
    response_model=ResponseUpsertResponse,
)
async def upsert_responses(
    session_id: str,
    payload: ResponseUpsertRequest,
    service: CoupleService = Depends(get_couple_service),
) -> ResponseUpsertResponse:
    try:
        response = service.upsert_responses(session_id, payload)
        service.db.commit()
    except Exception:
        service.db.rollback()
        raise
    return response


@router.get(
    "/sessions/{session_id}/responses",
    response_model=SavedResponses,
)
async def get_saved_responses(
    session_id: str,
    access_token: str,
    service: CoupleService = Depends(get_couple_service),
) -> SavedResponses:
    return service.fetch_responses(session_id, access_token)


@router.post(
    "/sessions/{session_id}/compute",
    response_model=CoupleResultEnvelope,
)
async def compute_result(
    session_id: str,
    payload: ComputeRequest,
    service: CoupleService = Depends(get_couple_service),
) -> CoupleResultEnvelope:
    # Ensure token is valid even though compute_result currently only
    # requires stage completion. This prevents arbitrary callers from
    # recomputing someone else's session.
    service._resolve_participant(session_id, payload.access_token)
    try:
        envelope = service.compute_result(session_id)
        service.db.commit()
    except Exception:
        service.db.rollback()
        raise
    return envelope
