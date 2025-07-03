from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class FriendInfo(BaseModel):
    name: str
    email: EmailStr
    description: Optional[str] = None

class MBTIResponse(BaseModel):
    friend_email: EmailStr
    evaluator_name: Optional[str] = None
    responses: dict  # {question_id: score}
    mbti_type: str
    scores: dict
    raw_scores: dict
    created_at: datetime

class FriendEvaluation(BaseModel):
    friend_email: EmailStr
    total_evaluations: int
    mbti_distribution: dict  # {mbti_type: count}
    average_scores: dict  # {E, I, S, N, T, F, J, P}
    recent_evaluations: List[MBTIResponse] 