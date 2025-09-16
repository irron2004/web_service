from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
import random

app = FastAPI(
    title="Calculate Service",
    description="초등수학문제를 제공하는 웹 서비스",
    version="1.0.0"
)

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="app/templates")

# 수학 문제 데이터
MATH_PROBLEMS = {
    "덧셈": [
        {"question": "15 + 23 = ?", "answer": 38},
        {"question": "47 + 18 = ?", "answer": 65},
        {"question": "32 + 45 = ?", "answer": 77},
        {"question": "56 + 29 = ?", "answer": 85},
        {"question": "78 + 34 = ?", "answer": 112}
    ],
    "뺄셈": [
        {"question": "45 - 12 = ?", "answer": 33},
        {"question": "67 - 23 = ?", "answer": 44},
        {"question": "89 - 34 = ?", "answer": 55},
        {"question": "123 - 45 = ?", "answer": 78},
        {"question": "156 - 67 = ?", "answer": 89}
    ],
    "곱셈": [
        {"question": "7 × 8 = ?", "answer": 56},
        {"question": "6 × 9 = ?", "answer": 54},
        {"question": "4 × 12 = ?", "answer": 48},
        {"question": "9 × 7 = ?", "answer": 63},
        {"question": "8 × 6 = ?", "answer": 48}
    ],
    "나눗셈": [
        {"question": "56 ÷ 7 = ?", "answer": 8},
        {"question": "72 ÷ 8 = ?", "answer": 9},
        {"question": "45 ÷ 5 = ?", "answer": 9},
        {"question": "63 ÷ 9 = ?", "answer": 7},
        {"question": "48 ÷ 6 = ?", "answer": 8}
    ]
}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/problems", response_class=HTMLResponse)
async def problems(request: Request, category: str = "덧셈"):
    """수학 문제 페이지"""
    problems = MATH_PROBLEMS.get(category, MATH_PROBLEMS["덧셈"])
    return templates.TemplateResponse("problems.html", {
        "request": request, 
        "category": category,
        "problems": problems
    })

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "message": "Calculate Service is running!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 