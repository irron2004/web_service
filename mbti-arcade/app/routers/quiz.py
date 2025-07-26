from fastapi import APIRouter, Request, Depends, HTTPException
from app.core.token import verify_token
from app.core.db import get_session
from app.core.services.mbti_service import MBTIService
from fastapi.templating import Jinja2Templates
from app.core.models_db import Pair
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/quiz", tags=["Quiz"])
templates = Jinja2Templates(directory="app/templates")

MBTI_QUESTIONS = [
    {"id": 1, "question": "새로운 사람들과 만나는 것을 좋아한다", "type": "E-I", "sign": 1},
    {"id": 2, "question": "혼자 있는 시간을 즐긴다", "type": "E-I", "sign": -1},
    {"id": 3, "question": "구체적이고 실용적인 정보를 선호한다", "type": "S-N", "sign": 1},
    {"id": 4, "question": "미래의 가능성과 새로운 아이디어에 관심이 많다", "type": "S-N", "sign": -1},
    {"id": 5, "question": "논리적이고 객관적인 판단을 한다", "type": "T-F", "sign": 1},
    {"id": 6, "question": "다른 사람의 감정을 고려하여 결정한다", "type": "T-F", "sign": -1},
    {"id": 7, "question": "계획을 세우고 그대로 실행하는 것을 좋아한다", "type": "J-P", "sign": 1},
    {"id": 8, "question": "즉흥적이고 유연한 생활을 선호한다", "type": "J-P", "sign": -1},
    {"id": 9, "question": "사람들과 함께 있을 때 에너지를 얻는다", "type": "E-I", "sign": 1},
    {"id": 10, "question": "조용한 환경에서 집중할 수 있다", "type": "E-I", "sign": -1},
    {"id": 11, "question": "현실적이고 구체적인 사실에 집중한다", "type": "S-N", "sign": 1},
    {"id": 12, "question": "직감과 영감을 믿는다", "type": "S-N", "sign": -1},
    {"id": 13, "question": "공정하고 일관된 기준을 적용한다", "type": "T-F", "sign": 1},
    {"id": 14, "question": "조화와 협력을 중시한다", "type": "T-F", "sign": -1},
    {"id": 15, "question": "정리정돈된 환경을 선호한다", "type": "J-P", "sign": 1},
    {"id": 16, "question": "자유롭고 개방적인 환경을 좋아한다", "type": "J-P", "sign": -1},
    {"id": 17, "question": "활발하고 적극적으로 대화한다", "type": "E-I", "sign": 1},
    {"id": 18, "question": "신중하고 깊이 있는 대화를 한다", "type": "E-I", "sign": -1},
    {"id": 19, "question": "실제 경험을 통해 배운다", "type": "S-N", "sign": 1},
    {"id": 20, "question": "이론과 개념을 통해 배운다", "type": "S-N", "sign": -1},
    {"id": 21, "question": "문제를 분석적으로 해결한다", "type": "T-F", "sign": 1},
    {"id": 22, "question": "사람들의 감정을 고려하여 문제를 해결한다", "type": "T-F", "sign": -1},
    {"id": 23, "question": "마감일을 지키는 것을 중요하게 생각한다", "type": "J-P", "sign": 1},
    {"id": 24, "question": "마감일을 유연하게 조정한다", "type": "J-P", "sign": -1}
]

RELATIONS_ENUM = ["friend", "boyfriend", "girlfriend", "spouse", "colleague", "family"]

@router.get("/{token}", response_class=HTMLResponse)
async def quiz_prefill(request: Request, token: str, session=Depends(get_session)):
    try:
        pair_id, my_mbti = verify_token(token)
    except ValueError:
        raise HTTPException(status_code=403, detail="expired link")
    
    svc = MBTIService(session)
    pair = await svc.session.get(Pair, pair_id)
    if not pair:
        raise HTTPException(status_code=404)
    
    return templates.TemplateResponse("mbti/friend_test.html",
          {"request": request, "pair_id": pair_id, "token": token,
           "friend_name": pair.my_name, "my_mbti": my_mbti,
           "questions": MBTI_QUESTIONS, "relations": RELATIONS_ENUM}) 