# MBTI Arcade

MBTI 성격 유형 테스트와 아케이드 게임을 결합한 웹 애플리케이션입니다.

## 🎯 기능

### MBTI 테스트
- **24문항** 5점 척도 설문
- **친구 평가**: 이름과 이메일로 친구 평가 수집
- **결과 분석**: 상세한 성격 유형 분석과 차트
- **통계**: 여러 평가 결과의 통계 및 추세

### 아케이드 게임
- **Snake**: 클래식 스네이크 게임
- **Tetris**: 테트리스 블록 게임  
- **Puzzle**: 숫자 퍼즐 게임

## 🛠 기술 스택

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, Tailwind CSS, HTMX, Alpine.js
- **Database**: JSON 파일 기반 인메모리 DB
- **Deployment**: Docker 지원

## 🚀 빠른 시작

### 로컬 개발
```bash
# 가상환경 생성
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn app.main:app --reload
```

### Docker 실행
```bash
docker build -t mbti-arcade .
docker run -p 8000:8000 mbti-arcade
```

## 📁 프로젝트 구조

```
mbti-arcade/
├── app/
│   ├── main.py           # FastAPI 앱 진입점
│   ├── database.py       # 데이터베이스 관리
│   ├── models.py         # 데이터 모델
│   ├── routers/          # API 라우터
│   │   ├── mbti.py       # MBTI 관련 엔드포인트
│   │   └── arcade.py     # 게임 관련 엔드포인트
│   ├── templates/        # HTML 템플릿
│   │   ├── mbti/         # MBTI 페이지들
│   │   └── arcade/       # 게임 페이지들
│   └── static/           # 정적 파일
├── requirements.txt      # Python 의존성
├── Dockerfile           # Docker 설정
└── test_mbti.py         # MBTI 테스트 스크립트
```

## 🎮 사용법

1. **MBTI 테스트**: `/mbti` - 개인 테스트
2. **친구 평가**: `/mbti/friend` - 친구 평가 입력
3. **게임**: `/arcade` - 아케이드 게임 모음

## 🧪 테스트

MBTI 점수 계산 로직 테스트:
```bash
python test_mbti.py
```

## 📊 API 엔드포인트

- `GET /` - 메인 페이지
- `GET /mbti` - MBTI 테스트
- `POST /mbti/submit` - 테스트 결과 제출
- `GET /mbti/friend` - 친구 평가 입력
- `POST /mbti/friend/submit` - 친구 평가 제출
- `GET /mbti/friend/results/{email}` - 친구 결과 조회
- `GET /arcade` - 게임 목록
- `GET /arcade/{game}` - 특정 게임

## 🔧 환경 변수

- `DATABASE_URL`: 데이터베이스 URL (선택사항)
- `SECRET_KEY`: 세션 암호화 키 (선택사항)

## 📝 배포

### Railway
```bash
railway login
railway init
railway up
```

### Render
- Root Directory: `mbti-arcade`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Vercel
```bash
vercel
```

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

MIT License 