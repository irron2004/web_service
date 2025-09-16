@echo off
chcp 65001 >nul
echo 🚀 MBTI & Arcade Web Service 시작 중...
echo.

REM 현재 디렉토리가 프로젝트 루트인지 확인
if not exist "app\main.py" (
    echo ❌ 오류: app\main.py 파일을 찾을 수 없습니다.
    echo 💡 mbti-arcade 디렉토리에서 실행해주세요.
    pause
    exit /b 1
)

REM Python이 설치되어 있는지 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 오류: Python이 설치되어 있지 않습니다.
    echo 💡 Python을 설치한 후 다시 시도해주세요.
    pause
    exit /b 1
)

REM 의존성 설치 확인
if not exist "venv" (
    echo 📦 가상환경이 없습니다. 생성 중...
    python -m venv venv
    echo ✅ 가상환경이 생성되었습니다.
)

REM 가상환경 활성화
echo 🔧 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM 의존성 설치
echo 📦 의존성 설치 중...
pip install -r requirements.txt

REM 서버 실행
echo 🚀 개발 서버 실행 중... (http://localhost:8000)
echo 💡 서버를 중지하려면 Ctrl+C를 누르세요.
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause 