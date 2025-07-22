from sqlmodel import Field, SQLModel
from datetime import datetime
from uuid import uuid4
from typing import Dict, Optional

class Friend(SQLModel, table=True):
    email: str = Field(primary_key=True, index=True)
    name: str
    description: Optional[str] = None
    actual_mbti: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    mbti_updated_at: Optional[datetime] = None

class Pair(SQLModel, table=True):
    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    friend_email: Optional[str] = Field(foreign_key="friend.email")
    mode: str
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Response(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pair_id: str = Field(foreign_key="pair.id", index=True)
    role: str
    answers: Dict[int, int]
    mbti_type: str
    scores: Dict[str, int]
    raw_scores: Dict[str, int]
    created_at: datetime = Field(default_factory=datetime.utcnow) 