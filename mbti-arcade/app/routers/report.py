from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.core.db import get_session
from app.core.token import verify_token
from app.core.services.mbti_service import MBTIService
from app.core.advice import build_advice

router = APIRouter(prefix="/api", tags=["Report"])

@router.get("/report/{token}")
async def report(token: str, session=Depends(get_session)):
    try:
        pair_id = verify_token(token)
    except ValueError:
        raise HTTPException(status_code=404, detail="invalid link")

    svc = MBTIService(session)
    data = await svc.get_pair_scores(pair_id)
    if not data:
        raise HTTPException(status_code=404, detail="no data")

    labels = ["E", "I", "S", "N", "T", "F", "J", "P"]
    return JSONResponse({"labels": labels, "datasets": data})

@router.get("/advice/{token}")
async def advice(token: str, session=Depends(get_session)):
    pid, my_mbti = verify_token(token)
    svc = MBTIService(session)
    data = await svc.get_pair_scores(pid)   # me + other
    if not data or len(data) < 2:
        raise HTTPException(404)
    mine, yours = sorted(data, key=lambda x: x["role"] == "other")
    advice = build_advice(mine["mbti"], yours["mbti"])
    return {"my_mbti": mine["mbti"], "your_mbti": yours["mbti"], "advice": advice} 