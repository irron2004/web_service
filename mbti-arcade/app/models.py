from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        nullable=False,
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    nickname: Mapped[str | None] = mapped_column(String(120))

    sessions: Mapped[List["Session"]] = relationship(back_populates="owner")


class Session(Base, TimestampMixin):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    invite_token: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    max_raters: Mapped[int] = mapped_column(Integer, default=50)

    owner: Mapped[User | None] = relationship(back_populates="sessions")
    self_responses: Mapped[List["SelfResponse"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    other_responses: Mapped[List["OtherResponse"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    aggregate: Mapped[Aggregate | None] = relationship(
        back_populates="session", uselist=False, cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    dim: Mapped[str] = mapped_column(String(4), nullable=False)
    sign: Mapped[int] = mapped_column(Integer, nullable=False)
    context: Mapped[str] = mapped_column(String(20), nullable=False)
    prompt_self: Mapped[str] = mapped_column(String(512), nullable=False)
    prompt_other: Mapped[str] = mapped_column(String(512), nullable=False)
    theme: Mapped[str] = mapped_column(String(60), nullable=False)
    scenario: Mapped[str] = mapped_column(String(120), nullable=False)


class SelfResponse(Base, TimestampMixin):
    __tablename__ = "responses_self"

    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sessions.id"), primary_key=True
    )
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("questions.id"), primary_key=True
    )
    value: Mapped[int] = mapped_column(Integer, nullable=False)

    session: Mapped[Session] = relationship(back_populates="self_responses")
    question: Mapped[Question] = relationship()


class OtherResponse(Base, TimestampMixin):
    __tablename__ = "responses_other"
    __table_args__ = (
        UniqueConstraint("session_id", "rater_hash", "question_id", name="uq_other"),
    )

    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sessions.id"), primary_key=True
    )
    rater_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("questions.id"), primary_key=True
    )
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    relation_tag: Mapped[str | None] = mapped_column(String(30))

    session: Mapped[Session] = relationship(back_populates="other_responses")
    question: Mapped[Question] = relationship()


class Aggregate(Base, TimestampMixin):
    __tablename__ = "aggregates"

    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sessions.id"), primary_key=True
    )
    ei_self: Mapped[float | None] = mapped_column(Float)
    sn_self: Mapped[float | None] = mapped_column(Float)
    tf_self: Mapped[float | None] = mapped_column(Float)
    jp_self: Mapped[float | None] = mapped_column(Float)
    ei_other: Mapped[float | None] = mapped_column(Float)
    sn_other: Mapped[float | None] = mapped_column(Float)
    tf_other: Mapped[float | None] = mapped_column(Float)
    jp_other: Mapped[float | None] = mapped_column(Float)
    ei_gap: Mapped[float | None] = mapped_column(Float)
    sn_gap: Mapped[float | None] = mapped_column(Float)
    tf_gap: Mapped[float | None] = mapped_column(Float)
    jp_gap: Mapped[float | None] = mapped_column(Float)
    ei_sigma: Mapped[float | None] = mapped_column(Float)
    sn_sigma: Mapped[float | None] = mapped_column(Float)
    tf_sigma: Mapped[float | None] = mapped_column(Float)
    jp_sigma: Mapped[float | None] = mapped_column(Float)
    n: Mapped[int] = mapped_column(Integer, default=0)
    gap_score: Mapped[float | None] = mapped_column(Float)

    session: Mapped[Session] = relationship(back_populates="aggregate")

