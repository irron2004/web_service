from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from app.core.db import get_session
from app.core.token import verify_token
from app.core.services.mbti_service import MBTIService
from app.core.advice import MBTIAdvice

router = APIRouter(prefix="/api", tags=["Report"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/report/{token}")
def report(token: str, session=Depends(get_session)):
    try:
        pair_id, my_mbti = verify_token(token)
    except ValueError:
        raise HTTPException(status_code=404, detail="invalid link")

    svc = MBTIService(session)
    data = svc.get_pair_scores(pair_id)
    if not data:
        raise HTTPException(status_code=404, detail="no data")

    labels = ["E", "I", "S", "N", "T", "F", "J", "P"]
    return JSONResponse({"labels": labels, "datasets": data})

@router.get("/advice/{token}")
def advice(token: str, session=Depends(get_session)):
    try:
        pair_id, my_mbti = verify_token(token)
    except ValueError:
        raise HTTPException(status_code=404, detail="invalid link")
    
    svc = MBTIService(session)
    data = svc.get_pair_scores(pair_id)   # me + other
    if not data or len(data) < 2:
        raise HTTPException(404)
    
    mine, yours = sorted(data, key=lambda x: x["role"] == "other")
    advice = MBTIAdvice.generate_advice(mine["mbti"], yours["mbti"], "friend", mine.get("scores", {}))
    return {"my_mbti": mine["mbti"], "your_mbti": yours["mbti"], "advice": advice} 