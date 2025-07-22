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
    # ... (24문항 정의, 기존과 동일) ...
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