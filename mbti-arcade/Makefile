# MBTI & Arcade Web Service Makefile

# Python 관련 변수
PYTHON = python
PIP = pip
UVICORN = uvicorn
PYTEST = pytest

# 프로젝트 관련 변수
APP_NAME = app.main:app
HOST = 0.0.0.0
PORT = 8000
DEV_PORT = 8001

# 가상환경 관련
VENV_NAME = venv
VENV_ACTIVATE = $(VENV_NAME)/Scripts/activate

# Docker 관련
DOCKER_IMAGE = mbti-arcade
DOCKER_CONTAINER = mbti-arcade-container

# 기본 타겟
.PHONY: help
help:
	@echo "MBTI & Arcade Web Service - 사용 가능한 명령어:"
	@echo ""
	@echo "개발 환경 설정:"
	@echo "  make install     - 의존성 설치"
	@echo "  make venv        - 가상환경 생성 및 활성화"
	@echo "  make setup       - 전체 개발 환경 설정"
	@echo ""
	@echo "서버 실행:"
	@echo "  make run         - 개발 서버 실행 (포트 8000)"
	@echo "  make dev         - 개발 서버 실행 (포트 8001)"
	@echo "  make prod        - 프로덕션 서버 실행"
	@echo ""
	@echo "테스트:"
	@echo "  make test        - 테스트 실행"
	@echo "  make test-verbose - 상세한 테스트 실행"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build - Docker 이미지 빌드"
	@echo "  make docker-run   - Docker 컨테이너 실행"
	@echo "  make docker-stop  - Docker 컨테이너 중지"
	@echo "  make docker-clean - Docker 이미지 및 컨테이너 정리"
	@echo ""
	@echo "유틸리티:"
	@echo "  make clean        - 캐시 파일 정리"
	@echo "  make format       - 코드 포맷팅"
	@echo "  make lint         - 코드 린팅"
	@echo "  make check        - 코드 품질 검사"

# 개발 환경 설정
.PHONY: install
install:
	@echo "📦 의존성 설치 중..."
	$(PIP) install -r requirements.txt

.PHONY: venv
venv:
	@echo "🐍 가상환경 생성 중..."
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "✅ 가상환경이 생성되었습니다."
	@echo "💡 가상환경을 활성화하려면:"
	@echo "   PowerShell: $(VENV_NAME)/Scripts/Activate.ps1"
	@echo "   Command Prompt: $(VENV_NAME)/Scripts/activate.bat"

.PHONY: setup
setup: venv
	@echo "🔧 전체 개발 환경 설정 중..."
	@echo "📦 의존성 설치 중..."
	$(PIP) install -r requirements.txt
	@echo "✅ 개발 환경 설정이 완료되었습니다!"

# 서버 실행
.PHONY: run
run:
	@echo "🚀 개발 서버 실행 중... (http://$(HOST):$(PORT))"
	$(PYTHON) -m $(UVICORN) $(APP_NAME) --reload --host $(HOST) --port $(PORT)

.PHONY: dev
dev:
	@echo "🚀 개발 서버 실행 중... (http://$(HOST):$(DEV_PORT))"
	$(PYTHON) -m $(UVICORN) $(APP_NAME) --reload --host $(HOST) --port $(DEV_PORT)

.PHONY: prod
prod:
	@echo "🚀 프로덕션 서버 실행 중... (http://$(HOST):$(PORT))"
	$(PYTHON) -m $(UVICORN) $(APP_NAME) --host $(HOST) --port $(PORT) --workers 4

# 테스트
.PHONY: test
test:
	@echo "🧪 테스트 실행 중..."
	$(PYTHON) -m $(PYTEST) test_mbti.py -v

.PHONY: test-verbose
test-verbose:
	@echo "🧪 상세한 테스트 실행 중..."
	$(PYTHON) -m $(PYTEST) test_mbti.py -v -s

# Docker 관련
.PHONY: docker-build
docker-build:
	@echo "🐳 Docker 이미지 빌드 중..."
	docker build -t $(DOCKER_IMAGE) .

.PHONY: docker-run
docker-run:
	@echo "🐳 Docker 컨테이너 실행 중... (http://localhost:$(PORT))"
	docker run -d --name $(DOCKER_CONTAINER) -p $(PORT):$(PORT) $(DOCKER_IMAGE)

.PHONY: docker-stop
docker-stop:
	@echo "🐳 Docker 컨테이너 중지 중..."
	docker stop $(DOCKER_CONTAINER) || true
	docker rm $(DOCKER_CONTAINER) || true

.PHONY: docker-clean
docker-clean: docker-stop
	@echo "🐳 Docker 이미지 및 컨테이너 정리 중..."
	docker rmi $(DOCKER_IMAGE) || true
	docker system prune -f

# 유틸리티
.PHONY: clean
clean:
	@echo "🧹 캐시 파일 정리 중..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	@echo "✅ 정리 완료!"

.PHONY: format
format:
	@echo "🎨 코드 포맷팅 중..."
	$(PYTHON) -m black app/ test_mbti.py
	$(PYTHON) -m isort app/ test_mbti.py

.PHONY: lint
lint:
	@echo "🔍 코드 린팅 중..."
	$(PYTHON) -m flake8 app/ test_mbti.py
	$(PYTHON) -m pylint app/ test_mbti.py

.PHONY: check
check: format lint test
	@echo "✅ 모든 검사 완료!"

# Windows PowerShell용 별칭
.PHONY: run-ps
run-ps:
	@echo "🚀 PowerShell에서 개발 서버 실행 중... (http://$(HOST):$(PORT))"
	powershell -Command "cd $(CURDIR); $(PYTHON) -m $(UVICORN) $(APP_NAME) --reload --host $(HOST) --port $(PORT)"

.PHONY: dev-ps
dev-ps:
	@echo "🚀 PowerShell에서 개발 서버 실행 중... (http://$(HOST):$(DEV_PORT))"
	powershell -Command "cd $(CURDIR); $(PYTHON) -m $(UVICORN) $(APP_NAME) --reload --host $(HOST) --port $(DEV_PORT)"

# 빠른 시작을 위한 별칭
.PHONY: start
start: run

.PHONY: quick
quick: install run 