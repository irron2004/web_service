# 🎮 MBTI & Arcade Web Service

MBTI 테스트와 아케이드 게임을 제공하는 웹 서비스입니다.

## 🚀 주요 기능

### 🧠 MBTI 테스트
- 24문항으로 정확한 MBTI 결과 분석
- Likert 5점 척도로 세밀한 성향 측정
- 제3자 관점의 객관적 질문 구성
- 16가지 MBTI 유형별 상세 설명
- 성향 분석 차트 및 백분율 제공
- 결과 공유 기능

### 🎯 아케이드 게임
- **스네이크 게임**: 클래식한 뱀 게임
- **테트리스**: 전설의 블록 게임
- **퍼즐 게임**: 숫자 슬라이딩 퍼즐

## 🛠️ 기술 스택

- **백엔드**: FastAPI (Python)
- **프론트엔드**: Jinja2 + HTMX + Alpine.js
- **스타일링**: Tailwind CSS
- **배포**: Docker
- **호스팅**: Railway/Render (권장)

## 📁 프로젝트 구조

```
web_service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 메인 애플리케이션
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── mbti.py          # MBTI 관련 라우터
│   │   └── arcade.py        # 아케이드 게임 라우터
│   └── templates/
│       ├── base.html        # 기본 템플릿
│       ├── index.html       # 메인 홈페이지
│       ├── mbti/            # MBTI 관련 템플릿
│       │   ├── index.html
│       │   ├── test.html
│       │   └── result.html
│       └── arcade/          # 아케이드 게임 템플릿
│           ├── index.html
│           ├── snake.html
│           ├── tetris.html
│           └── puzzle.html
├── requirements.txt         # Python 의존성
├── Dockerfile              # Docker 설정
├── .dockerignore           # Docker 제외 파일
└── README.md               # 프로젝트 설명
```

## 🚀 로컬 개발 환경 설정

### 1. 저장소 클론
```bash
git clone <repository-url>
cd web_service
```

### 2. 가상환경 생성 및 활성화
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 서버 실행
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 브라우저에서 확인
```
http://localhost:8000
```

## 🐳 Docker 배포

### 1. Docker 이미지 빌드
```bash
docker build -t mbti-arcade-service .
```

### 2. Docker 컨테이너 실행
```bash
docker run -p 8000:8000 mbti-arcade-service
```

## 🌐 클라우드 배포

### Railway 배포 (권장)
1. [Railway](https://railway.app) 계정 생성
2. GitHub 저장소 연결
3. 자동 배포 설정
4. 도메인 연결

### Render 배포
1. [Render](https://render.com) 계정 생성
2. GitHub 저장소 연결
3. Web Service 생성
4. 환경 변수 설정

## 📊 API 엔드포인트

### 메인 페이지
- `GET /` - 메인 홈페이지
- `GET /health` - 헬스 체크

### MBTI 관련
- `GET /mbti` - MBTI 테스트 홈페이지
- `GET /mbti/test` - MBTI 테스트 페이지
- `POST /mbti/result` - MBTI 결과 처리
- `GET /mbti/types` - MBTI 유형 설명

### 아케이드 게임
- `GET /arcade` - 아케이드 게임 홈페이지
- `GET /arcade/snake` - 스네이크 게임
- `GET /arcade/tetris` - 테트리스 게임
- `GET /arcade/puzzle` - 퍼즐 게임

## 🎮 게임 조작법

### 스네이크 게임
- **방향키** 또는 **WASD**: 뱀 이동
- **게임 시작**: 시작 버튼 클릭
- **일시정지**: 일시정지 버튼 클릭

### 테트리스
- **←→**: 블록 좌우 이동
- **↓**: 블록 빠른 하강
- **스페이스바**: 블록 회전
- **게임 시작**: 시작 버튼 클릭

### 퍼즐 게임
- **마우스 클릭**: 타일 이동
- **섞기**: 퍼즐 섞기
- **해답 보기**: 완성된 퍼즐 보기

## 💰 수익화 (Google AdSense)

1. 사이트 완성 후 [Google AdSense](https://www.google.com/adsense) 신청
2. 승인 후 `app/templates/base.html`의 주석 처리된 AdSense 코드 활성화
3. 수익 발생!

## 🔧 개발 팁

### 새로운 게임 추가
1. `app/routers/arcade.py`에 라우트 추가
2. `app/templates/arcade/`에 템플릿 생성
3. `app/templates/arcade/index.html`에 게임 링크 추가

### MBTI 질문 수정
`app/routers/mbti.py`의 `MBTI_QUESTIONS` 배열 수정

### 스타일 수정
Tailwind CSS 클래스 사용하여 `app/templates/` 내 HTML 파일 수정

## 📝 라이선스

MIT License

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.

---

**즐거운 MBTI 테스트와 게임 되세요! 🎮✨**

# Web Service Collection

여러 웹페이지를 한 곳에서 관리하는 저장소입니다.

## 📁 프로젝트 구조

```
web_service/
├── mbti-arcade/          # MBTI 테스트 + 아케이드 게임
│   ├── app/              # FastAPI 애플리케이션
│   ├── requirements.txt  # Python 의존성
│   ├── Dockerfile        # Docker 설정
│   └── test_mbti.py      # MBTI 테스트 스크립트
├── README.md             # 이 파일
└── .gitignore           # Git 무시 파일
```

## 🎯 현재 프로젝트

### MBTI Arcade (`mbti-arcade/`)
- **기술 스택**: FastAPI, Python, HTML, Tailwind CSS, HTMX, Alpine.js
- **기능**: 
  - MBTI 성격 유형 테스트 (24문항, 5점 척도)
  - 친구 평가 기능 (이름/이메일 입력)
  - 아케이드 게임 (Snake, Tetris, Puzzle)
  - 결과 통계 및 차트
- **배포**: Railway, Render, Vercel 등

## 🚀 새로운 프로젝트 추가하기

새로운 웹페이지를 추가하려면:

1. 루트에 새 폴더 생성 (예: `portfolio/`, `blog/`, `dashboard/`)
2. 각 폴더에 독립적인 웹 애플리케이션 구성
3. 각각 별도로 배포 가능

## 📋 배포 가이드

각 프로젝트는 독립적으로 배포할 수 있습니다:

### Railway 배포
```bash
cd mbti-arcade
railway login
railway init
railway up
```

### Render 배포
- Render 대시보드에서 새 Web Service 생성
- GitHub 저장소 연결
- Root Directory를 `mbti-arcade`로 설정

### Vercel 배포
```bash
cd mbti-arcade
vercel
```

## 🔧 개발 환경

각 프로젝트는 독립적인 개발 환경을 가집니다:

```bash
# MBTI Arcade 개발
cd mbti-arcade
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 📝 프로젝트 추가 예시

### 포트폴리오 웹사이트
```
portfolio/
├── index.html
├── styles.css
└── script.js
```

### 블로그
```
blog/
├── app/
├── requirements.txt
└── Dockerfile
```

### API 서버
```
api/
├── app/
├── requirements.txt
└── Dockerfile
```

## 🤝 기여하기

각 프로젝트는 독립적으로 관리되며, 필요에 따라 공통 라이브러리를 `shared/` 폴더에 추가할 수 있습니다.

## 📄 라이선스

MIT License 