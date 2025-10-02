# Calculate Service (Standalone)

교육용 사칙연산 문제를 제공하는 FastAPI 서비스입니다. 기존 monorepo에서 분리해 독립적으로 실행·배포할 수 있도록 구성했습니다.

## 주요 기능
- `/` · `/problems` HTML 화면: 카테고리별 연산 문제 제공, 즉시 채점 UI
- `/api/problems`: 카테고리 필터가 가능한 JSON API (RFC 9457 문제 상세 응답)
- `/api/categories`: 사용 가능한 문제 카테고리 나열
- 모든 응답은 `X-Request-ID` 헤더를 보존하며, `X-Robots-Tag: noindex`로 검색 노출을 차단

## 빠른 시작
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
make dev                   # 의존성 + 테스트 의존성 설치
make run                   # http://localhost:8000
```

## 설정
환경 변수는 `.env` 파일로 오버라이드할 수 있습니다.

| 환경 변수 | 설명 | 기본값 |
|-----------|------|--------|
| `APP_NAME` | 서비스명 | Calculate Service |
| `APP_DESCRIPTION` | OpenAPI 설명 | 초등수학 문제 제공 API |
| `ENABLE_OPENAPI` | 문서 노출 여부 (`true`/`false`) | true |
| `ALLOWED_PROBLEM_CATEGORIES` | 쉼표로 구분된 허용 카테고리 | 모든 카테고리 |

## 테스트
```bash
make test
```
테스트는 FastAPI `TestClient`를 사용해 `X-Request-ID` 전파, RFC 9457 오류 응답, noindex 헤더를 검증합니다.

## 배포 메모
- Docker 빌드는 `Dockerfile`을 그대로 사용할 수 있습니다.
- Cloud Run/Cloudflare 배포 시 `X-Request-ID` 헤더를 그대로 전달하도록 프록시를 구성하세요.
- 관측: 기본 로거(`calculate_service`)는 요청 소요 시간과 상태 코드를 출력합니다. 필요 시 OpenTelemetry 익스포터를 여기에 연동할 수 있습니다.

## 디렉터리 구조
```
app/
  __init__.py        # FastAPI 앱 생성 (라우터/미들웨어 연결)
  config.py          # Pydantic Settings 기반 설정 로더
  instrumentation.py # X-Request-ID, noindex 헤더를 처리하는 미들웨어
  problem_bank.py    # 카테고리·문제 데이터 정의 및 헬퍼
  routers/           # HTML/JSON 라우터 모듈
  templates/, static/ # Jinja 템플릿과 정적 자산
```

## 라이선스
MIT
