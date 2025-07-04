# 통합 Web Service Docker 설정

이 설정은 Web Service Hub, Math App, MBTI Arcade 프로젝트를 하나의 Docker Compose로 실행합니다.

## 서비스 구성

### Web Service Hub (메인)
- **URL**: http://localhost:8080
- **역할**: 모든 서비스를 관리하는 중앙 허브

### Math App
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000

### MBTI Arcade
- **Service**: http://localhost:8001

## 사용법

### 1. 전체 서비스 실행

```bash
# 프로젝트 루트 디렉토리에서
docker-compose up --build
```

### 2. 특정 서비스만 실행

```bash
# 메인 허브만 실행
docker-compose up main-hub

# Math App만 실행
docker-compose up math-backend math-frontend

# MBTI Arcade만 실행
docker-compose up mbti-arcade

# Backend만 실행
docker-compose up math-backend mbti-arcade
```

### 3. 백그라운드 실행

```bash
docker-compose up -d --build
```

### 4. 로그 확인

```bash
# 전체 로그
docker-compose logs

# 특정 서비스 로그
docker-compose logs main-hub
docker-compose logs math-backend
docker-compose logs math-frontend
docker-compose logs mbti-arcade

# 실시간 로그
docker-compose logs -f
```

## 포트 설정

| 서비스 | 내부 포트 | 외부 포트 | URL |
|--------|-----------|-----------|-----|
| Main Hub | 8080 | 8080 | http://localhost:8080 |
| Math Backend | 8000 | 8000 | http://localhost:8000 |
| Math Frontend | 80 | 3000 | http://localhost:3000 |
| MBTI Arcade | 8000 | 8001 | http://localhost:8001 |

## 네트워크

모든 서비스는 `web-service-network`라는 Docker 네트워크를 통해 통신합니다.

## 개발 모드

볼륨 마운트가 설정되어 있어 코드 변경사항이 즉시 반영됩니다:

```bash
# 개발 모드로 실행
docker-compose up --build
```

## 환경 변수

### Main Hub
- 기본 환경 변수 사용

### Math Backend
- `DATABASE_URL`: 데이터베이스 연결 문자열

### MBTI Arcade
- 기본 환경 변수 사용

## 문제 해결

### 포트 충돌
다른 서비스와 포트가 충돌하는 경우:

```yaml
# docker-compose.yml에서 포트 변경
ports:
  - "8081:8080"  # Main Hub
  - "8002:8000"  # Math Backend
  - "3001:80"    # Math Frontend  
  - "8003:8000"  # MBTI Arcade
```

### 빌드 실패
```bash
# 캐시 없이 다시 빌드
docker-compose build --no-cache

# 특정 서비스만 다시 빌드
docker-compose build --no-cache main-hub
```

### 컨테이너 상태 확인
```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 컨테이너 상세 정보
docker-compose top
```

## 정리

```bash
# 컨테이너 중지 및 제거
docker-compose down

# 이미지까지 제거
docker-compose down --rmi all

# 볼륨까지 제거
docker-compose down -v
```

## 개별 서비스 접근

### Web Service Hub (메인)
- 메인 페이지: http://localhost:8080
- 모든 서비스의 중앙 관리 포인트

### Math App
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api

### MBTI Arcade
- 메인 페이지: http://localhost:8001
- MBTI 테스트: http://localhost:8001/mbti
- 아케이드 게임: http://localhost:8001/arcade

## 프로덕션 배포

프로덕션 환경에서는 다음을 고려하세요:

1. 환경 변수 설정
2. 데이터베이스 백업
3. SSL/TLS 설정
4. 로드 밸런서 설정
5. 모니터링 및 로깅
6. 리소스 제한 설정 