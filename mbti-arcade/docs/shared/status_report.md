# 360Me 서비스 통합 현황 리포트 (시니어 개발자용)

작성일: 2025-09-19
작성자: Codex (calculate_math 분리 작업 기반)

---

## 1. 제품 비전 & 범위 요약
- **핵심 목표**: “If I were you” 인식 차이를 부부/커플 맥락으로 확장해 오해 → 이해 → 합의를 돕는 안전한 대화 컨테이너 제공. ([`PRD`](../mbti-arcade/docs/PRD.md))
- **3단계 플로우**: ① 기존 perception gap 요약(타인지표, k≥3), ② SELF/GUESS 이중 설문, ③ 부부 심층 설문 및 Δ·플래그 계산. (`PRD` R-101~R-108)
- **산출물**: 8축 하위척도 + Δ 히트맵, Top-3 이슈 카드, 주간 실습 가이드, 결정 패킷(decision_packet)으로 결과 봉인. (`PRD` R-103~R-113)
- **비기능 요구**: API P95 <1s, Web Vitals(LCP≤2.5s/INP≤200ms/CLS≤0.1), WCAG 2.2 AA, X-Request-ID/OTel 100% 전파, k≥3 익명성. (`PRD` §5)

---

## 2. 레포지토리 구조 & 서비스 경계
```
web_service_new/
├─ mbti-arcade/        # Core perception-gap FastAPI + SQLAlchemy (프로덕션 백엔드)
├─ main-service/       # 허브/랜딩 FastAPI (Jinja)
├─ calculate_math/  # (신규) 독립 FastAPI 계산 서비스 (calculate_math로 이관)
├─ nginx/              # 로컬 reverse proxy 샘플
├─ docs/               # PRD, DeploymentPlan, 운영 가이드, 본 리포트 등
└─ docker-compose.yml  # 메인 허브 + mbti-arcade 통합 실행 (calculate/math 별도 배포)
```
- **mbti-arcade**: 설문, 세션, 결과, OG 카드 등 모든 핵심 API·데이터. Alembic, OpenTelemetry, RFC 9457 오류 구조 유지. (README.md, mbti-arcade/docs/DeploymentPlan.md)
- **main-service**: 허브 페이지와 서비스 링크, Health endpoint. (README.md)
- **calculate_math/frontend**: React 학습 게임 UI (별도 저장소).
- **calculate_math/app**: FastAPI + SQLite 통합 서비스(별도 저장소).

---

## 3. calculate_math 분리 상태
### 3.1 코드 구조 (새로 정리됨)
- `app/__init__.py`: FastAPI 앱 팩토리 (`create_app`) + Static/Jinja 마운트.
- `app/config.py`: Pydantic Settings(`.env` 지원) → 앱 메타데이터, 카테고리 화이트리스트 제어.
- `app/instrumentation.py`: `RequestContextMiddleware`로 X-Request-ID 부여, `X-Robots-Tag: noindex`, `Cache-Control: no-store`, 요청 로그 수집.
- `app/problem_bank.py`: dataclass 기반 사칙연산 문제 정의 + 조회 헬퍼.
- `app/routers/pages.py`: `/`, `/problems` HTML 렌더.
- `app/routers/problems.py`: `/api/categories`, `/api/problems` JSON API (RFC 9457 오류 응답).
- `tests/test_api.py`: Health, 기본 카테고리, invalid 카테고리, X-Request-ID, noindex 헤더 검증.
- `requirements(-dev).txt`, `pyproject.toml`, `Makefile`, `.env.example`, `README.md` 추가로 독립 설치/테스트 흐름 완비.

### 3.2 빌드/배포
- `Dockerfile` 그대로 활용 가능 (Python 3.11 slim).
- `Makefile` → `make dev`(전체 의존성), `make run`, `make test`.
- `README.md`에 빠른 시작, 설정 환경변수, 관측성 주의사항 명시.

### 3.3 모노레포 연동 상태
- `docker-compose.yml`에서 math-app 서비스 제거 → 기본 스택은 `main-hub`, `mbti-arcade`만 기동 (math/calc는 별도 저장소).
- `nginx/conf.d/default.conf`에서 `/calculate` 라우팅 제거.
- `README.md`, `README-Docker-Integrated.md`, `docs/senior_brief.md`, `mbti-arcade/AGENTS.md` 등 문서에서 “독립 서비스”로 표기 업데이트.

### 3.4 단일 도메인 임시 연결 전략
- **임시 버튼 추가**: `mbti-arcade/app/templates/` 내 원하는 템플릿(Jinja)에 `/calculate` 링크 버튼 삽입.
- **프록시 재등록**: 단일 도메인 하위 경로로 노출이 필요하면 `nginx/conf.d/default.conf`에 기존 `/calculate` 블록을 복원하거나 Cloudflare Workers/Pages Rules로 프록시. (현재 블록은 주석처리 없이 삭제됨 → 필요 시 Git history 참고해 빠르게 재도입 가능.)
- **HTTP 연동**: 서버사이드 호출이 필요하면 `requests` 등으로 `calculate_math` API 사용 (현재 RFC 9457, X-Request-ID 준수).
- **분리 준비**: 서비스 내부 의존성 제거, 설정/문서 독립 확보, 테스트 분리 완료 → 나중에 별도 리포지토리로 이동하거나 CI/CD 파이프라인을 분리하기 쉬운 상태.

---

## 4. 개발 진행 상황 (서비스별)
### 4.1 mbti-arcade (핵심 백엔드)
- FastAPI + SQLAlchemy + Alembic. 세션/응답/결과/OG 이미지 라우터 구비.
- RFC 9457, X-Request-ID, OpenTelemetry, k≥3 safeguard 등 골든 룰 준수. (README.md, docs/testing.md, mbti-arcade/docs/Claude.md)
- 테스트: `mbti-arcade/tests/`에 E2E/통합/legacy 스위트 존재. `make check`로 Black/isort/flake8/pylint/pytest 일괄 실행.
- 배포 계획: Cloud Run 컨테이너, Cloud SQL, Secrets, OpenTelemetry. (mbti-arcade/docs/DeploymentPlan.md)

### 4.2 main-service (허브)
- FastAPI + Jinja 템플릿. 각 서비스 링크 제공, `/health` 존재.
- Dockerfile, requirements 업데이트됨 (이전 커밋 참고). 현재 문서에는 허브 운영 방안 명시. (README.md, README-Docker-Integrated.md)

### 4.3 calculate_math (학습용)
- 프론트엔드: React + TypeScript (Vite) — `calculate_math/frontend`.
- 백엔드: FastAPI + SQLite — `calculate_math/app`.
- 별도 저장소: https://github.com/irron2004/calculate_math (로컬에 `calculate_math/` 디렉터리로 체크아웃).

### 4.4 calculate_math (본 작업)
- 독립 패키지화 완료, 테스트 샘플 존재. `X-Robots-Tag`, `X-Request-ID` 헤더 보장.
- 단일 도메인 환경에서도 프록시만 붙이면 공존 가능. 향후 별도 도메인 또는 서브도메인 이전 용이.

---

## 5. 인프라 & 배포 전략 (mbti-arcade/docs/DeploymentPlan.md 기반)
- **Frontend**: Cloudflare Pages, `npm run build` → `dist/`, 커스텀 도메인 `app.360me.app`.
- **Backend**: Cloud Run (asia-northeast3), Artifact Registry 이미지, Blue/Green/Canary 전환.
- **Database**: Cloud SQL (PostgreSQL) + Cloud Run 보안 커넥터.
- **Secrets**: Google Secret Manager → Cloud Run 환경변수.
- **CDN/WAF**: Cloudflare DNS + WAF, Rate Limit, Bot Fight. API 경로 BYPASS 캐시.
- **CI/CD**: GitHub Actions (fe-deploy, be-deploy 워크플로 예시 제공).
- **Observability**: OpenTelemetry → GCP Logging/Trace, 대시보드(P95, Error Rate, Web Vitals, GapScore 상태) 필수.
- **SEO/Ads**: `X-Robots-Tag`/noindex 적용, `ads.txt`, OG 이미지 API (Satori/Sharp) 계획.
- **롤백**: Cloud Run 리비전 즉시 전환, 릴리즈 체크리스트에 RFC9457/k≥3/Web Vitals 포함.

---

## 6. 품질·보안·관측 정책 (mbti-arcade/AGENTS.md, docs/testing.md, mbti-arcade/docs/Claude.md)
- **코딩 스타일**: Python Black/isort/flake8/pylint, Jinja 템플릿 일관성.
- **테스트 전략**: pytest 유닛/통합/E2E + Web Vitals + Axe 접근성 + k6 성능.
- **보안**: TLS, Token 링크 만료, noindex, PII 최소화, AdSense confirmed-click 회피.
- **관측성**: X-Request-ID, OpenTelemetry 스팬, 로그/트레이스 조인율 ≥99%. `docs/testing.md`에 검증 매트릭스.
- **가드레일**: k<3 공유 금지, 안전 안내 루틴, 의사결정 패킷 기록.

---

## 7. 현재 위험·의존성·TODO
- **calculate_math 재연결**: 단일 도메인 운영 중이라면 `/calculate` 프록시를 다시 붙이는 작업 필요. 추후 완전 분리를 염두에 두고 버튼·링크만 건드릴 것.
- **mbti-arcade P0**: [`Tasks`](../mbti-arcade/docs/product/Tasks.md) 기준 Self→Invite→Aggregate, observability, OG 이미지, Decision Packet 등 남은 작업 존재.
- **CI/CD 분리**: calculate_math 전용 빌드/배포 파이프라인은 아직 없음 → 추후 Cloud Run/Pages/별도 호스팅 결정 필요.
- **문서 싱크**: 본 리포트 외에도 `mbti-arcade/docs/DeploymentPlan.md` / `mbti-arcade/docs/PRD.md` 업데이트 시 동기화 필요.
- **테스트 실행**: calculate_math 분리 후 `make test` 로컬 확인 필요(현재는 실행 로그 없음).

---

## 8. 단기 액션 아이템 (권장)
1. **프록시 복구 & 버튼 추가**: 단일 도메인 유지 중이면 `nginx/conf.d/default.conf`에 `/calculate` 라우팅 복원 후 `mbti-arcade` 템플릿에 CTA 삽입.
2. **테스트 수행**: `calculate_math` 디렉터리에서 `make dev && make test` 실행해 새 구조 검증.
3. **CI 파이프라인 설계**: 분리 서비스용 GitHub Actions 워크플로(빌드/배포) 추가, Artifact Registry or 별도 컨테이너 레지스트리 결정.
4. **관측 연동 계획 수립**: RequestContextMiddleware를 OpenTelemetry/구조화 로깅과 연결.
5. **Documentation Sync**: 본 리포트를 `docs/` 인덱스에 추가 링크, 향후 변경 시 본 문서 갱신 절차 정의.

---

## 9. 참고 문서
- `README.md` — 제품 개요, 서비스 맵, 로컬 개발 방법.
- `mbti-arcade/docs/PRD.md` — Couple Insight 기능/NFR/마일스톤/지표.
- `mbti-arcade/docs/DeploymentPlan.md` — Cloudflare Pages + Cloud Run 배포 전략.
- `docs/senior_brief.md` — 아키텍처 하이라이트, 즉시 다음 작업.
- `docs/testing.md` — 테스트·관측·성능 검증 매트릭스.
- `mbti-arcade/AGENTS.md` — 기여자 가이드, 개발 표준.
- `calculate_math/README.md` — 신규 독립 서비스 사용법.


---

## 10. PM Follow-up & Decisions (calculate_math)

<!-- ⟦L137–L274⟧: 360Me PM Follow-up & Decisions (2025-09-30) -->

### 10.1 Decisions (2025-09-30)
- **Error format**: 전 서비스 **RFC 9457 Problem Details** 통일, 성공 응답은 **평문 JSON**.
- **Cloud scope**: **GCP 단일 표준**(Cloud Run, Cloud SQL, Artifact Registry, Secret Manager).
- **Domain/SEO**: 커플 서비스( `app.360me.app` 등 )는 **index 허용**, `calculate_math`는 `calc.360me.app` + **noindex/아동 보호**.

### 10.2 Sprint Focus (W1–W4)
- **W1**: RFC9457 핸들러, `X-Request-ID`, OTel 스타트팩 → `mbti-arcade`, `main-service`, `calculate_math` 적용.
- **W2**: Cloud Run 스테이징 빌드/릴리즈 워크플로 통일, Blue/Green 롤백 런북 정리.
- **W3**: Δ/flag 계산 안정화, decision_packet 봉인, Playwright E2E 아티팩트.
- **W4**: `calculate_math` Cloud Run 배포(`calc.360me.app`), 부하·보안 점검.

### 10.3 Shared Observability Scaffolding
- 공통 라이브러리: `libs/observability` (ProblemDetails, RequestID, OTel 초기화).
- 계약: `X-Request-ID` 요청/응답/로그/스팬 100% 전파.
- NFR: API p95 < 1s, 에러율 < 1%, Web Vitals(LCP≤2.5s / INP≤200ms / CLS≤0.1).

### 10.4 Recommended Next Actions
1. 세 서비스에 공통 핸들러·미들웨어 적용.
2. Cloud Run 스테이징 파이프라인과 Artifact Registry 이미지 플로 정비.
3. `calculate_math`는 `noindex` 유지 + AdSense 비개인화 광고, `ads.txt` 공개.

### 10.5 Change Summary 스니펫 (PR용)
- **Docs only**: 위 결정/스프린트/Observability/Next Actions를 L137–L274에 추가.
- **Tests**: 없음 (문서 변경).
- **Out-of-scope**: 코드/CI 변경은 별도 PR에서.

### 10.6 Migration & Alignment Notes
- **calculate_math** 성공 응답을 평문 JSON으로 전환, 오류는 RFC9457 공통 핸들러 사용.
- `RequestIDMiddleware` + `install_problem_details`를 세 서비스 모두에 주입.
- `calc.360me.app` 서브도메인으로 Cloud Run 배포, `X-Robots-Tag: noindex` 유지.
- FE 래퍼 의존부는 API 어댑터 레이어에서 호환 처리.

### 10.7 CI Guardrail 예시 (paths-filter)
```yml
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      docs: ${{ steps.filter.outputs.docs }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            docs:
              - 'docs/**'
              - '**/*.md'

  test-backend:
    needs: changes
    if: needs.changes.outputs.docs != 'true'
    runs-on: ubuntu-latest
    steps: { ... }

  lint-docs:
    needs: changes
    if: needs.changes.outputs.docs == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx markdownlint-cli2 **/*.md
```

### 10.8 Follow-up Checklist
- [`Tasks`](../mbti-arcade/docs/product/Tasks.md): P0 ~ P1 항목(공통 핸들러, RequestID/OTel, Cloud Run 스테이징, calc 도메인 분리) 추가.
- `mbti-arcade/docs/DeploymentPlan.md`/README: GCP 단일 전략, Cloud Run·Secret Manager·경로필터 명시.
- 커밋 메시지 예: `docs(status-report): log pm decisions for error/GCP/domain standards`.

> 결정은 즉시 유효하며, 공통 라이브러리 PR과 calculate_math 응답 포맷 전환 PR은 별도로 진행합니다.
