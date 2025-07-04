from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import os

from app.routers import mbti, arcade

app = FastAPI(
    title="MBTI & Arcade Service",
    description="MBTI 테스트와 아케이드 게임을 제공하는 웹 서비스",
    version="1.0.0"
)

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="app/templates")

# 라우터 등록
app.include_router(mbti.router, prefix="/mbti", tags=["MBTI"])
app.include_router(arcade.router, prefix="/arcade", tags=["Arcade"])

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return RedirectResponse(url="http://localhost:8080")

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "message": "MBTI & Arcade Service is running!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 