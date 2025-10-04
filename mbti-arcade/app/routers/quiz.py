from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.db import get_session
from app.core.models_db import Pair
from app.core.services.mbti_service import MBTIService
from app.core.token import verify_token

router = APIRouter(prefix="/quiz", tags=["Quiz"])
TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# 실제 데이터베이스 질문 ID를 사용 (각 차원당 6개씩 24개)
MBTI_QUESTIONS = [
    {"id": 1, "question": "새로운 사람들과 만나는 것을 좋아한다", "type": "E-I", "sign": 1},
    {"id": 2, "question": "혼자 있는 시간을 즐긴다", "type": "E-I", "sign": -1},
    {"id": 101, "question": "사람들과 함께 있을 때 에너지를 얻는다", "type": "E-I", "sign": 1},
    {"id": 102, "question": "조용한 환경에서 집중할 수 있다", "type": "E-I", "sign": -1},
    {"id": 201, "question": "활발하고 적극적으로 대화한다", "type": "E-I", "sign": 1},
    {"id": 202, "question": "신중하고 깊이 있는 대화를 한다", "type": "E-I", "sign": -1},
    {"id": 3, "question": "구체적이고 실용적인 정보를 선호한다", "type": "S-N", "sign": 1},
    {"id": 4, "question": "미래의 가능성과 새로운 아이디어에 관심이 많다", "type": "S-N", "sign": -1},
    {"id": 103, "question": "현실적이고 구체적인 사실에 집중한다", "type": "S-N", "sign": 1},
    {"id": 104, "question": "직감과 영감을 믿는다", "type": "S-N", "sign": -1},
    {"id": 203, "question": "실제 경험을 통해 배운다", "type": "S-N", "sign": 1},
    {"id": 204, "question": "이론과 개념을 통해 배운다", "type": "S-N", "sign": -1},
    {"id": 5, "question": "논리적이고 객관적인 판단을 한다", "type": "T-F", "sign": 1},
    {"id": 6, "question": "다른 사람의 감정을 고려하여 결정한다", "type": "T-F", "sign": -1},
    {"id": 105, "question": "공정하고 일관된 기준을 적용한다", "type": "T-F", "sign": 1},
    {"id": 106, "question": "조화와 협력을 중시한다", "type": "T-F", "sign": -1},
    {"id": 205, "question": "문제를 분석적으로 해결한다", "type": "T-F", "sign": 1},
    {"id": 206, "question": "사람들의 감정을 고려하여 문제를 해결한다", "type": "T-F", "sign": -1},
    {"id": 301, "question": "계획을 세우고 그대로 실행하는 것을 좋아한다", "type": "J-P", "sign": 1},
    {"id": 302, "question": "즉흥적이고 유연한 생활을 선호한다", "type": "J-P", "sign": -1},
    {"id": 401, "question": "정리정돈된 환경을 선호한다", "type": "J-P", "sign": 1},
    {"id": 402, "question": "자유롭고 개방적인 환경을 좋아한다", "type": "J-P", "sign": -1},
    {"id": 501, "question": "마감일을 지키는 것을 중요하게 생각한다", "type": "J-P", "sign": 1},
    {"id": 502, "question": "마감일을 유연하게 조정한다", "type": "J-P", "sign": -1}
]

RELATIONS_ENUM = ["friend", "boyfriend", "girlfriend", "spouse", "colleague", "family"]

def render_invite_page(request: Request, token: str, session) -> HTMLResponse:
    try:
        pair_id, my_mbti = verify_token(token)
    except ValueError:
        raise HTTPException(status_code=403, detail="expired link")

    svc = MBTIService(session)
    pair = svc.session.get(Pair, pair_id)
    if not pair:
        raise HTTPException(status_code=404)

    return templates.TemplateResponse(
        "mbti/friend_test.html",
        {
            "request": request,
            "pair_id": pair_id,
            "token": token,
            "friend_name": pair.my_name,
            "my_mbti": my_mbti,
            "questions": MBTI_QUESTIONS,
            "relations": RELATIONS_ENUM,
        },
    )


@router.get("/{token}", response_class=HTMLResponse, name="quiz_prefill")
def quiz_prefill(request: Request, token: str, session=Depends(get_session)):
    return render_invite_page(request, token, session)
