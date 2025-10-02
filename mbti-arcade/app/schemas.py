from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

DIMENSIONS = ("EI", "SN", "TF", "JP")


class QuestionSchema(BaseModel):
    id: int
    code: str
    dim: str
    sign: int
    context: str
    prompt_self: str
    prompt_other: str
    theme: str
    scenario: str

    @field_validator("dim")
    @classmethod
    def validate_dim(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in DIMENSIONS:
            raise ValueError(f"Unsupported dimension '{value}'")
        return normalized

    @field_validator("sign")
    @classmethod
    def validate_sign(cls, value: int) -> int:
        if value not in (-1, 1):
            raise ValueError("sign must be -1 or 1")
        return value


class SessionCreate(BaseModel):
    owner_email: Optional[EmailStr] = None
    owner_nickname: Optional[str] = Field(default=None, max_length=120)
    mode: str = Field(pattern="^(basic|couple|friend|work|partner|family)$")
    max_raters: int = Field(default=50, ge=1, le=500)
    expires_in_hours: int = Field(default=72, ge=1, le=720)
    anonymous: bool = True


class SessionResponse(BaseModel):
    session_id: str
    invite_token: str
    expires_at: datetime
    mode: str
    max_raters: int
    anonymous: bool


class InviteUpdate(BaseModel):
    session_id: str
    expires_in_hours: Optional[int] = Field(default=None, ge=1, le=720)
    max_raters: Optional[int] = Field(default=None, ge=1, le=500)
    anonymous: Optional[bool] = None


class AnswerItem(BaseModel):
    question_id: int
    value: int = Field(ge=1, le=5)


class SelfSubmitRequest(BaseModel):
    session_id: str
    answers: List[AnswerItem]


class SelfSubmitResponse(BaseModel):
    session_id: str
    self_norm: Dict[str, float]
    self_radar: Dict[str, float]


class OtherSubmitRequest(BaseModel):
    invite_token: str
    answers: List[AnswerItem]
    relation_tag: Optional[str] = Field(default=None, max_length=30)
    rater_key: Optional[str] = Field(default=None, max_length=120)


class OtherSubmitResponse(BaseModel):
    session_id: str
    accepted: bool
    respondents: int


class ResultDetail(BaseModel):
    session_id: str
    mode: str
    n: int
    self_norm: Dict[str, float]
    other_norm: Optional[Dict[str, float]]
    gap: Optional[Dict[str, float]]
    sigma: Optional[Dict[str, float]]
    gap_score: Optional[float]
    radar_self: Dict[str, float]
    radar_other: Optional[Dict[str, float]]


class ProblemDetails(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    errors: Optional[Dict[str, List[str]]] = None
