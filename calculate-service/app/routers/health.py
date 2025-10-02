from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Service health check")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "message": "Calculate Service is running"}


__all__ = ["router"]
