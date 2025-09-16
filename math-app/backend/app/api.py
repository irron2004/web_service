from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import random
from datetime import date
from pydantic import BaseModel
import hashlib
from sqlalchemy.orm import Session
from . import models
from .db import get_db

router = APIRouter()

# Pydantic 모델들
class LoginRequest(BaseModel):
    nickname: str
    password: str

class LoginResponse(BaseModel):
    user_id: int
    nickname: str
    role: str
    message: str

class ProblemCreate(BaseModel):
    left: int
    right: int
    answer: int
    options: List[int]

class SessionCreate(BaseModel):
    user_id: int = None  # 게스트는 None
    problems: List[ProblemCreate]

class ProblemResponse(BaseModel):
    id: int
    left: int
    right: int
    answer: int
    options: List[int]

class SessionResponse(BaseModel):
    session_id: int
    problems: List[ProblemResponse]

def hash_password(password: str) -> str:
    """비밀번호를 SHA-256으로 해시"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_problem_options(correct_answer: int) -> List[int]:
    """정답을 포함한 4개의 선택지를 생성"""
    options = [correct_answer]
    
    # 정답과 다른 선택지들 생성
    while len(options) < 4:
        # 정답의 ±10 범위 내에서 랜덤 선택
        offset = random.randint(-10, 10)
        wrong_answer = correct_answer + offset
        
        # 0보다 작으면 양수로 조정
        if wrong_answer < 0:
            wrong_answer = abs(wrong_answer)
        
        # 중복되지 않는 선택지만 추가
        if wrong_answer not in options:
            options.append(wrong_answer)
    
    # 선택지 순서 섞기
    random.shuffle(options)
    return options

def generate_grade_appropriate_problem() -> Dict[str, int]:
    """두 자리 수 이상의 덧셈 문제 생성 (10~99 + 10~99)"""
    # 두 자리 숫자 범위: 10~99
    left = random.randint(10, 99)
    right = random.randint(10, 99)
    answer = left + right
    return {"left": left, "right": right, "answer": answer}

@router.post("/v1/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """닉네임+비밀번호로 로그인/계정 생성"""
    password_hash = hash_password(request.password)
    
    # 기존 사용자 검색
    user = db.query(models.User).filter(models.User.nickname == request.nickname).first()
    
    if user:
        # 기존 사용자: 비밀번호 확인
        if user.password_hash == password_hash:
            return LoginResponse(
                user_id=user.id,
                nickname=user.nickname,
                role=user.role,
                message="로그인 성공"
            )
        else:
            raise HTTPException(status_code=401, detail="비밀번호가 틀렸습니다")
    else:
        # 새 사용자: 계정 생성
        new_user = models.User(
            nickname=request.nickname,
            password_hash=password_hash,
            role="student"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return LoginResponse(
            user_id=new_user.id,
            nickname=new_user.nickname,
            role=new_user.role,
            message="새 계정이 생성되었습니다"
        )

@router.post("/v1/sessions", response_model=SessionResponse)
def create_session():
    """20문제 세트 생성 및 반환"""
    problems = []
    
    for i in range(20):
        # 문제 생성
        problem_data = generate_grade_appropriate_problem()
        
        # 선택지 생성
        options = generate_problem_options(problem_data["answer"])
        
        # 문제 객체 생성
        problem = ProblemResponse(
            id=i + 1,  # 임시 ID (실제로는 DB에서 생성)
            left=problem_data["left"],
            right=problem_data["right"],
            answer=problem_data["answer"],
            options=options
        )
        problems.append(problem)
    
    # 세션 응답 생성
    session_response = SessionResponse(
        session_id=random.randint(1000, 9999),  # 임시 세션 ID
        problems=problems
    )
    
    return session_response

@router.patch("/v1/problems/{problem_id}")
def update_problem(problem_id: int, chosen_answer: int, attempt_no: int = 1):
    """문제 답안 제출 및 결과 반환"""
    # 실제로는 DB에서 문제를 조회하고 정답을 확인해야 함
    # 현재는 임시 응답
    
    # 임시로 정답을 7로 가정 (실제로는 DB에서 조회)
    correct_answer = 7
    
    is_correct = chosen_answer == correct_answer
    
    return {
        "problem_id": problem_id,
        "chosen_answer": chosen_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct,
        "attempt_no": attempt_no,
        "message": "정답입니다!" if is_correct else "틀렸습니다. 다시 시도해보세요."
    }

@router.get("/v1/stats/daily")
def get_daily_stats(days: int = 30):
    """최근 30일 기록"""
    # 임시 데이터 반환
    return {
        "total_sessions": 15,
        "total_problems": 300,
        "average_accuracy": 85.5,
        "average_time": 1200,  # 초 단위
        "streak_days": 7
    }

@router.post("/v1/alerts/daily")
def send_daily_alert():
    """목표 달성 메일 발송"""
    return {"message": "Daily alert sent successfully"} 