from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}


@router.get("/readyz")
async def readyz():
    return {"status": "ready"}
