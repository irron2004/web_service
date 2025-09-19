#!/usr/bin/env python3
"""
MBTI 점수 계산 로직 테스트 스크립트
"""

import pytest
from app.core.services.mbti_service import MBTIService
from app.core.models_db import SQLModel
from app.core.db import engine, SessionLocal
from app.core.token import issue_token, verify_token

@pytest.fixture(scope="module")
def db_session():
    SQLModel.metadata.create_all(engine)
    with SessionLocal() as sess:
        yield sess

def test_token_roundtrip():
    pid = "test123"
    token = issue_token(pid)
    assert verify_token(token) == pid

def test_calc_ei_positive(db_session):
    svc = MBTIService(db_session)
    answers = {1:5,2:1,3:5,4:1,5:5,6:1}  # E/I 편향
    mbti, scores, raw = svc._calc_scores(answers, [
        {"id": 1, "type": "E-I", "sign": 1},
        {"id": 2, "type": "E-I", "sign": -1},
        {"id": 3, "type": "E-I", "sign": 1},
        {"id": 4, "type": "E-I", "sign": -1},
        {"id": 5, "type": "E-I", "sign": 1},
        {"id": 6, "type": "E-I", "sign": -1},
    ])
    assert mbti[0] == "E" and scores["E"] > scores["I"] 