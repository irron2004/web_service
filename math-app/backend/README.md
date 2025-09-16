# Math App Backend

FastAPI 기반 초등 연산(덧셈) 학습 서비스 백엔드

## 실행 방법

1. 의존성 설치

```bash
pip install -r requirements.txt
```

2. 개발 서버 실행

```bash
uvicorn app.main:app --reload
```

3. 환경 변수 설정
- .env 파일에 DATABASE_URL 등 필요시 추가

## 폴더 구조

```
backend/
  app/
    main.py         # FastAPI 엔트리포인트
    models.py       # SQLAlchemy ORM 모델
    db.py           # DB 연결
    api.py          # API 라우터
    __init__.py
  requirements.txt
  README.md
```

## 주요 기능 (MVP)
- 20문제 세트 생성 및 기록
- 정/오답 즉시 피드백
- 학습 기록 저장 및 통계
- 보호자 메일 알림 (AWS SES) 