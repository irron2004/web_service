from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.core.db import get_session
from app.core.token import verify_token
from app.core.services.mbti_service import MBTIService

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