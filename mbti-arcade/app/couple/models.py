"""Database models dedicated to the couple perception-gap flow."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models import TimestampMixin


class CoupleSession(Base, TimestampMixin):
    __tablename__ = "couple_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    stage: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    a_self_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    a_guess_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    b_self_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    b_guess_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    stage3_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    k_threshold: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    k_value: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    k_visible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    stage1_snapshot: Mapped[dict | None] = mapped_column(JSON, default=None)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_computed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    participants: Mapped[list["CoupleParticipant"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    responses: Mapped[list["CoupleResponse"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    result: Mapped[CoupleResult | None] = relationship(
        back_populates="session", uselist=False, cascade="all, delete-orphan"
    )
    decision_packets: Mapped[list["DecisionPacket"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    audit_events: Mapped[list["AuditEvent"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class CoupleParticipant(Base, TimestampMixin):
    __tablename__ = "couple_participants"
    __table_args__ = (
        UniqueConstraint("session_id", "role", name="uq_participant_role"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("couple_sessions.id"))
    role: Mapped[str] = mapped_column(String(1), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(255))
    access_token: Mapped[str] = mapped_column(
        String(64), default=lambda: uuid4().hex, unique=True, nullable=False
    )

    session: Mapped[CoupleSession] = relationship(back_populates="participants")
    responses: Mapped[list["CoupleResponse"]] = relationship(
        back_populates="participant", cascade="all, delete-orphan"
    )


class CoupleResponse(Base, TimestampMixin):
    __tablename__ = "couple_responses"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "participant_id",
            "question_code",
            "kind",
            name="uq_response_unique",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("couple_sessions.id"))
    participant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("couple_participants.id"), nullable=False
    )
    question_code: Mapped[str] = mapped_column(String(12), nullable=False)
    kind: Mapped[str] = mapped_column(String(10), nullable=False)  # self | guess
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    stage: Mapped[int] = mapped_column(Integer, nullable=False, default=2)

    session: Mapped[CoupleSession] = relationship(back_populates="responses")
    participant: Mapped[CoupleParticipant] = relationship(back_populates="responses")


class CoupleResult(Base, TimestampMixin):
    __tablename__ = "couple_results"

    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("couple_sessions.id"), primary_key=True
    )
    scales: Mapped[dict[str, dict[str, float]] | None] = mapped_column(JSON, nullable=True)
    deltas: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    flags: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    insights: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    top_delta_items: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    gap_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    session: Mapped[CoupleSession] = relationship(back_populates="result")


class DecisionPacket(Base, TimestampMixin):
    __tablename__ = "decision_packets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("couple_sessions.id"))
    packet_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    storage_url: Mapped[str | None] = mapped_column(String(255))
    code_ref: Mapped[str | None] = mapped_column(String(64))
    model_id: Mapped[str | None] = mapped_column(String(64))

    session: Mapped[CoupleSession] = relationship(back_populates="decision_packets")


class AuditEvent(Base, TimestampMixin):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("couple_sessions.id"), nullable=True
    )
    req_id: Mapped[str | None] = mapped_column(String(64))
    actor: Mapped[str | None] = mapped_column(String(120))
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON)
    prev_hash: Mapped[str | None] = mapped_column(String(64))
    hash: Mapped[str] = mapped_column(String(64), nullable=False)
    code_ref: Mapped[str | None] = mapped_column(String(64))

    session: Mapped[CoupleSession | None] = relationship(back_populates="audit_events")
