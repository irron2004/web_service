from sqlmodel import Field, SQLModel
from datetime import datetime
from uuid import uuid4
from typing import Dict, Optional
from sqlalchemy import JSON

class Friend(SQLModel, table=True):
    email: str = Field(primary_key=True, index=True)
    name: str
    description: Optional[str] = None
    actual_mbti: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    mbti_updated_at: Optional[datetime] = None

class Pair(SQLModel, table=True):
    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    mode: str                      # self | friend
    friend_email: str | None = Field(foreign_key="friend.email")
    my_name: str | None = None
    my_email: str | None = None
    my_mbti: str | None = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Response(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pair_id: str = Field(foreign_key="pair.id", index=True)
    role: str            # "me" | "other"
    relation: str | None = None   # friend | boyfriend | ...
    answers: str = Field(sa_column=JSON)  # JSON string으로 저장
    mbti_type: str
    scores: str = Field(sa_column=JSON)   # JSON string으로 저장
    raw_scores: str = Field(sa_column=JSON)  # JSON string으로 저장
    created_at: datetime = Field(default_factory=datetime.utcnow) 