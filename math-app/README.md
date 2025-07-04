# 수학 놀이터 (Math Playground)

1-2학년 학생들을 위한 태블릿 친화적인 수학 학습 웹 애플리케이션입니다.

## 🎯 프로젝트 개요

이 프로젝트는 초등학교 1-2학년 학생들이 재미있게 수학을 학습할 수 있도록 설계된 웹 애플리케이션입니다. 학생, 부모, 선생님이 각각의 역할에 맞는 기능을 사용할 수 있습니다.

## 🚀 주요 기능

### 학생 기능
- 🎮 **수학 게임**: 덧셈, 뺄셈, 곱셈 문제 풀이
- 📊 **진도 확인**: 학습 현황 및 통계 확인
- 🏆 **성취도**: 배지 및 성취 시스템
- ⏰ **타이머**: 시간 제한이 있는 문제 풀이
- 🔥 **연속 정답**: 연속 정답 보너스 시스템

### 부모 기능
- 👨‍👩‍👧‍👦 **자녀 현황**: 자녀들의 학습 현황 모니터링
- 🔔 **알림**: 자녀의 학습 완료 및 성적 향상 알림
- 📈 **통계**: 전체 학습 통계 확인

### 선생님 기능
- 👥 **학생 관리**: 전체 학생 현황 관리
- 📊 **학년별 통계**: 학년별 학습 통계 확인
- 💬 **메시지**: 학생들에게 메시지 전송

## 🛠 기술 스택

### 백엔드
- **FastAPI** - Python 웹 프레임워크
- **PostgreSQL** - 관계형 데이터베이스
- **SQLAlchemy** - ORM
- **Pydantic** - 데이터 검증
- **Python 3.8+** - 프로그래밍 언어

### 프론트엔드
- **React 18** - 사용자 인터페이스 라이브러리
- **TypeScript** - 타입 안전성
- **Vite** - 빠른 개발 서버 및 빌드 도구
- **React Router** - 클라이언트 사이드 라우팅
- **Lucide React** - 아이콘 라이브러리
- **CSS3** - 스타일링

## 📁 프로젝트 구조

```
math-app/
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI 앱 설정
│   │   ├── api.py          # API 라우터
│   │   ├── models.py       # 데이터베이스 모델
│   │   └── db.py           # 데이터베이스 설정
│   ├── requirements.txt    # Python 의존성
│   └── README.md           # 백엔드 문서
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/     # React 컴포넌트
│   │   ├── contexts/       # React Context
│   │   ├── types/          # TypeScript 타입
│   │   ├── utils/          # 유틸리티 함수
│   │   ├── App.tsx         # 메인 앱
│   │   └── main.tsx        # 진입점
│   ├── package.json        # Node.js 의존성
│   └── README.md           # 프론트엔드 문서
└── README.md               # 프로젝트 문서
```

## 🚀 설치 및 실행

### 필수 요구사항
- Python 3.8+
- Node.js 16.0+
- PostgreSQL 12+
- npm 또는 yarn

### 1. 저장소 클론
```bash
git clone <repository-url>
cd math-app
```

### 2. 백엔드 설정
```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export DATABASE_URL="postgresql://username:password@localhost/math_app"
export SECRET_KEY="your-secret-key"

# 데이터베이스 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload
```

### 3. 프론트엔드 설정
```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

### 4. 브라우저에서 확인
- 프론트엔드: http://localhost:5173
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 👥 데모 계정

### 학생 계정
- **사용자명**: student1
- **비밀번호**: password
- **학년**: 1학년

### 부모 계정
- **사용자명**: parent1
- **비밀번호**: password
- **자녀**: 김철수 (1학년)

### 선생님 계정
- **사용자명**: teacher1
- **비밀번호**: password
- **관리 학생**: 3명

## 🎮 게임 규칙

### 수학 게임
- **문제 수**: 10문제
- **제한 시간**: 문제당 30초
- **점수 계산**: 기본 10점 + 남은 시간 보너스
- **연속 정답**: 연속 정답 시 추가 보너스
- **학년별 난이도**:
  - 1학년: 덧셈, 뺄셈
  - 2학년: 덧셈, 뺄셈, 곱셈

### 학습 세션 규칙
- 하루 최대 3세션
- 세션 간 30분 휴식
- 주말에는 제한 없음

## 📊 데이터 모델

### 주요 엔티티
- **User**: 사용자 정보 (학생/부모/선생님)
- **MathProblem**: 수학 문제
- **GameSession**: 게임 세션 기록
- **StudentProgress**: 학생 진도
- **ParentNotification**: 부모 알림
- **TeacherReport**: 선생님 리포트

## 🔧 개발 가이드

### 백엔드 개발
1. API 엔드포인트 추가: `app/api.py`
2. 데이터 모델 수정: `app/models.py`
3. 마이그레이션 생성: `alembic revision --autogenerate -m "description"`
4. 테스트 실행: `pytest`

### 프론트엔드 개발
1. 새 컴포넌트 생성: `src/components/`
2. 타입 정의 추가: `src/types/index.ts`
3. 스타일링: 컴포넌트별 CSS 파일
4. 테스트 실행: `npm test`

## 🚀 배포

### 백엔드 배포 (Docker)
```bash
cd backend
docker build -t math-app-backend .
docker run -p 8000:8000 math-app-backend
```

### 프론트엔드 배포
```bash
cd frontend
npm run build
# dist 폴더를 웹 서버에 배포
```

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해 주세요.

## 🎯 로드맵

### v1.1 (예정)
- [ ] 다국어 지원 (영어, 중국어)
- [ ] 음성 피드백
- [ ] 더 많은 수학 문제 유형
- [ ] 모바일 앱 버전

### v1.2 (예정)
- [ ] AI 기반 난이도 조절
- [ ] 부모-자녀 소통 기능
- [ ] 학습 리포트 생성
- [ ] 게임화 요소 추가

---

**수학 놀이터**로 재미있게 수학을 배워보세요! 🎓✨ 