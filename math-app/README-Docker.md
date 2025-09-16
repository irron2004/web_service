# Math App Docker 설정

이 프로젝트는 Docker를 사용하여 Frontend와 Backend를 컨테이너화했습니다.

## 파일 구조

```
math-app/
├── backend/
│   ├── Dockerfile          # Backend 컨테이너 설정
│   └── ...
├── frontend/
│   ├── Dockerfile          # Frontend 컨테이너 설정
│   ├── nginx.conf          # Nginx 설정
│   └── ...
├── docker-compose.yml      # 전체 서비스 오케스트레이션
├── .dockerignore           # Docker 빌드 시 제외할 파일들
└── README-Docker.md        # 이 파일
```

## 사용법

### 1. 전체 서비스 실행 (권장)

```bash
# 프로젝트 루트 디렉토리에서
docker-compose up --build
```

이 명령어로 다음이 실행됩니다:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

### 2. 개별 서비스 실행

#### Backend만 실행
```bash
cd backend
docker build -t math-app-backend .
docker run -p 8000:8000 math-app-backend
```

#### Frontend만 실행
```bash
cd frontend
docker build -t math-app-frontend .
docker run -p 3000:80 math-app-frontend
```

### 3. 개발 모드

개발 중에는 볼륨 마운트를 사용하여 코드 변경사항을 즉시 반영할 수 있습니다:

```bash
docker-compose up --build
```

## 환경 변수

### Backend 환경 변수
- `DATABASE_URL`: 데이터베이스 연결 문자열 (기본값: sqlite:///./math_app.db)

### Frontend 환경 변수
- 프록시 설정을 통해 Backend API에 자동 연결

## 네트워크

서비스들은 `math-app-network`라는 Docker 네트워크를 통해 통신합니다:
- Frontend → Backend: `http://backend:8000`

## 문제 해결

### 포트 충돌
다른 서비스가 8000번이나 3000번 포트를 사용 중인 경우:
```bash
# docker-compose.yml에서 포트 변경
ports:
  - "8001:8000"  # Backend
  - "3001:80"    # Frontend
```

### 빌드 실패
```bash
# 캐시 없이 다시 빌드
docker-compose build --no-cache
```

### 컨테이너 로그 확인
```bash
# 전체 로그
docker-compose logs

# 특정 서비스 로그
docker-compose logs backend
docker-compose logs frontend
```

## 프로덕션 배포

프로덕션 환경에서는 다음을 고려하세요:

1. 환경 변수 설정
2. 데이터베이스 백업
3. SSL/TLS 설정
4. 로드 밸런서 설정
5. 모니터링 및 로깅

## 정리

```bash
# 컨테이너 중지 및 제거
docker-compose down

# 이미지까지 제거
docker-compose down --rmi all

# 볼륨까지 제거
docker-compose down -v
``` 