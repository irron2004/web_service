# Calculate Service 개요

Calculate Service는 초등 수학 사칙연산 학습을 돕는 FastAPI 기반 마이크로서비스로, HTML 웹 화면과 JSON API를 동시에 제공하도록 설계되었습니다. 본 문서는 서비스 구성, 핵심 기능, 설정, 운용 포인트를 정리합니다.

## 아키텍처와 구성 요소
- **FastAPI 애플리케이션 팩토리**: `create_app()`은 설정을 불러와 FastAPI 인스턴스를 생성하고 라우터·미들웨어·정적 자산을 연결합니다. HTML 템플릿은 Jinja2를 사용하며 `/static` 경로에 정적 파일을 마운트합니다.【F:calculate-service/app/__init__.py†L12-L34】
- **설정 로더**: Pydantic Settings 기반 `Settings` 클래스는 앱 이름, 설명, 버전, OpenAPI 노출 여부, 허용 카테고리를 환경 변수로 제어할 수 있도록 지원합니다.【F:calculate-service/app/config.py†L7-L23】
- **관측 미들웨어**: `RequestContextMiddleware`는 모든 요청에 `X-Request-ID`를 부여·전파하고 처리 시간, 상태 코드 등을 로그에 남기며, HTML/JSON 응답에 `X-Robots-Tag: noindex`와 `Cache-Control: no-store` 헤더를 설정합니다.【F:calculate-service/app/instrumentation.py†L1-L41】
- **문제 은행**: `Problem` 데이터클래스와 `_PROBLEM_DATA` 매핑을 통해 덧셈·뺄셈·곱셈·나눗셈 문제를 제공하며, 카테고리 목록과 문제 조회 유틸리티를 제공합니다.【F:calculate-service/app/problem_bank.py†L1-L47】【F:calculate-service/app/problem_bank.py†L49-L60】

## 주요 엔드포인트
- **헬스체크**: `/health`에서 서비스 상태를 반환합니다.【F:calculate-service/app/routers/health.py†L1-L9】
- **HTML 페이지**: `/`와 `/problems`는 허용된 카테고리 목록과 선택된 카테고리의 문제를 템플릿으로 렌더링합니다. 카테고리 쿼리 파라미터가 없거나 지원되지 않는 경우 첫 번째 허용 카테고리를 사용합니다.【F:calculate-service/app/routers/pages.py†L1-L43】
- **카테고리 API**: `/api/categories`는 사용 가능한 카테고리와 개수를 반환합니다.【F:calculate-service/app/routers/problems.py†L1-L21】
- **문제 API**: `/api/problems`는 카테고리별 문제 목록과 총 개수를 제공하며, 카테고리가 없거나 잘못된 경우 RFC 9457 형식의 오류 응답을 반환합니다.【F:calculate-service/app/routers/problems.py†L23-L60】

## 설정 및 커스터마이징
- `.env`를 통해 앱 이름, 설명, OpenAPI 문서 노출, 허용 카테고리를 조정할 수 있습니다.【F:calculate-service/app/config.py†L7-L23】
- `ALLOWED_PROBLEM_CATEGORIES`를 지정하면 HTML·API 모두 해당 목록으로 필터링됩니다. 값이 비어 있는 경우 문제 은행의 기본 카테고리를 사용합니다.【F:calculate-service/app/routers/pages.py†L10-L18】【F:calculate-service/app/routers/problems.py†L12-L20】

## 테스트와 품질 보증
- `tests/test_api.py`는 헬스 엔드포인트, 기본 카테고리 선택, 잘못된 카테고리 처리, `X-Request-ID` 헤더 전파, HTML 라우트의 `noindex` 헤더를 검증합니다.【F:calculate-service/tests/test_api.py†L34-L70】
- `Makefile`의 `make test` 타깃을 통해 FastAPI `TestClient` 기반 테스트를 실행할 수 있습니다.【F:calculate-service/README.md†L24-L28】

## 배포 참고 사항
- Dockerfile을 사용해 컨테이너 이미지를 빌드하고, Cloud Run/Cloudflare 등 프록시 환경에서는 `X-Request-ID` 헤더를 보존하도록 구성합니다.【F:calculate-service/README.md†L30-L36】
- 기본 로거(`calculate_service`)가 요청 메트릭을 남기므로 필요 시 OpenTelemetry 익스포터를 연동해 확장할 수 있습니다.【F:calculate-service/app/instrumentation.py†L1-L41】【F:calculate-service/README.md†L35-L36】

## 시작 방법
```bash
python -m venv .venv
source .venv/bin/activate
make dev
make run  # http://localhost:8000
```
위 커맨드는 가상환경 구성, 개발 의존성 설치, 로컬 실행을 순차적으로 돕습니다.【F:calculate-service/README.md†L12-L23】

## 요약
Calculate Service는 학습용 사칙연산 문제를 안정적으로 제공하기 위해 구성된 경량 FastAPI 서비스입니다. 설정 가능성과 관측 가능성을 갖추고 있으며, HTML UI와 JSON API를 동시에 지원해 교육 콘텐츠를 유연하게 활용할 수 있습니다.
