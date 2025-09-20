"""Pydantic schemas for the couple perception-gap API."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

class ParticipantCreate(BaseModel):
    role: str = Field(pattern="^[AB]$")
    nickname: Optional[str] = Field(default=None, max_length=120)
    email: Optional[str] = Field(default=None, max_length=255)


class StageOneSnapshot(BaseModel):
    k: int = Field(ge=0)
    visible: bool = False
    dimensions: Dict[str, float] = Field(default_factory=dict)


class CoupleSessionCreate(BaseModel):
    participants: List[ParticipantCreate] = Field(default_factory=list, max_items=2)
    k_threshold: int = Field(default=3, ge=1, le=10)
    stage1_snapshot: Optional[StageOneSnapshot] = None


class ParticipantEnvelope(BaseModel):
    role: str
    nickname: Optional[str]
    email: Optional[str]
    access_token: str


class KState(BaseModel):
    threshold: int
    current: int
    visible: bool


class CoupleSessionEnvelope(BaseModel):
    session_id: str
    stage: int
    participants: List[ParticipantEnvelope]
    a_self_completed: bool
    a_guess_completed: bool
    b_self_completed: bool
    b_guess_completed: bool
    stage3_completed: bool
    k_state: KState
    stage1_snapshot: Optional[StageOneSnapshot]
    created_at: datetime
    updated_at: datetime


class AnswerPayload(BaseModel):
    code: str = Field(pattern="^[A-Z0-9-]+$", max_length=12)
    value: int = Field(ge=0, le=10)


class ResponseUpsertRequest(BaseModel):
    access_token: str
    stage: int = Field(default=2, ge=2, le=3)
    self_answers: List[AnswerPayload]
    guess_answers: List[AnswerPayload]


class ResponseUpsertResponse(BaseModel):
    session_id: str
    role: str
    stage: int
    self_completed: bool
    guess_completed: bool
    stage_progress: Dict[str, bool]


class SavedResponses(BaseModel):
    session_id: str
    role: str
    self_answers: Dict[str, int]
    guess_answers: Dict[str, int]


class DecisionPacketDescriptor(BaseModel):
    packet_sha256: str
    created_at: datetime
    code_ref: Optional[str] = None
    model_id: Optional[str] = None


class CoupleResultEnvelope(BaseModel):
    session_id: str
    scales: Dict[str, Dict[str, Dict[str, float]]]
    deltas: Dict[str, Dict[str, float]]
    flags: List[Dict[str, str]]
    insights: List[Dict[str, str | float]]
    top_delta_items: List[str]
    gap_summary: Dict[str, float | str | None]
    k_state: KState
    decision_packet: Optional[DecisionPacketDescriptor]
    generated_at: datetime


class ComputeRequest(BaseModel):
    access_token: str
