# MBTI & Arcade Web Service PowerShell 실행 스크립트

Write-Host "🚀 MBTI & Arcade Web Service 시작 중..." -ForegroundColor Green
Write-Host ""

# 현재 디렉토리가 프로젝트 루트인지 확인
if (-not (Test-Path "app\main.py")) {
    Write-Host "❌ 오류: app\main.py 파일을 찾을 수 없습니다." -ForegroundColor Red
    Write-Host "💡 mbti-arcade 디렉토리에서 실행해주세요." -ForegroundColor Yellow
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

# Python이 설치되어 있는지 확인
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python 버전: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 오류: Python이 설치되어 있지 않습니다." -ForegroundColor Red
    Write-Host "💡 Python을 설치한 후 다시 시도해주세요." -ForegroundColor Yellow
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

# 가상환경 확인 및 생성
if (-not (Test-Path "venv")) {
    Write-Host "📦 가상환경이 없습니다. 생성 중..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ 가상환경이 생성되었습니다." -ForegroundColor Green
}

# 가상환경 활성화
Write-Host "🔧 가상환경 활성화 중..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# 의존성 설치
Write-Host "📦 의존성 설치 중..." -ForegroundColor Yellow
pip install -r requirements.txt

# 서버 실행
Write-Host "🚀 개발 서버 실행 중... (http://localhost:8000)" -ForegroundColor Green
Write-Host "💡 서버를 중지하려면 Ctrl+C를 누르세요." -ForegroundColor Cyan
Write-Host ""

try {
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
} catch {
    Write-Host "❌ 서버 실행 중 오류가 발생했습니다." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "👋 서버가 종료되었습니다." -ForegroundColor Yellow
    Read-Host "계속하려면 Enter를 누르세요"
} 