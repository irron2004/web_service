**요약(3–5줄)**
프런트엔드 정적 리소스는 Cloudflare Pages에 배포해 전세계 엣지에서 서빙하고, FastAPI 백엔드는 컨테이너 이미지로 Cloud Run에 올립니다. 상태 데이터는 Cloud SQL for PostgreSQL에 저장하며, 캐시·WAF·SSL은 Cloudflare에서 통합 관리합니다. GitHub Actions로 CI/CD를 구성하고 Cloud Run 리비전 트래픽 스플릿으로 Blue/Green·Canary 롤아웃을 수행합니다. 비밀은 Secret Manager로 주입하고 OpenTelemetry로 로그·트레이스를 표준화합니다. ([Cloudflare Docs][1])

```yaml
---
version: "1.0"
date: "2025-09-18"
environments: ["dev", "stg", "prod"]
regions:
  be: "asia-northeast3"
  db: "asia-northeast3"
domains:
  web: "app.360me.app"
  api: "api.360me.app"
owner: "PM · 이지율"
source_of_truth: "DeploymentPlan.md"
---
```

### 0) 아키텍처 요약(ASCII)

```
[User]
  │
  ▼
[Cloudflare DNS+CDN+WAF]───►(Pages) FE: React/Vite 정적
  │                         (Custom domains/SSL)
  └──► /api/*  ───────────► (Cloud Run) FastAPI 컨테이너
                             ├─ Cloud SQL(PostgreSQL)
                             ├─ Redis(옵션: Memorystore)
                             └─ OTel Exporter → GCP(Trace/Logging)
```

* **FE:** Cloudflare Pages로 Vite `dist/`를 서빙, 커스텀 도메인과 자동 SSL 지원. ([Cloudflare Docs][1])
* **BE:** Cloud Run 컨테이너 리비전 배포·롤백·트래픽 스플릿. ([Google Cloud][2])
* **DB:** Cloud SQL(PostgreSQL) + Cloud Run 보안 커넥터. ([Google Cloud][3])
* **리전:** 한국 타깃은 서울(`asia-northeast3`) 권고. ([Google Cloud][4])

---

## 1) 환경/도메인 전략

* **환경:** `dev` → 내부 개발, `stg` → 퍼블릭 베타, `prod` → 실서비스.
* **도메인:** FE `app.360me.app` (Cloudflare Pages 커스텀 도메인), API `api.360me.app` (Cloudflare DNS → Cloud Run HTTPS 매핑). ([Cloudflare Docs][5])

---

## 2) 프런트엔드 배포 — Cloudflare Pages

* **빌드 명령/출력:** `npm run build` → `dist/` (Vite 정적 배포). ([vitejs][6])
* **Pages 설정:** Git 연동 → Build `npm run build`, Output `dist/`, 자동 SSL + 커스텀 도메인 연결. ([Cloudflare Docs][1])
* **캐시:** 해시된 정적 자산은 `Cache-Control: public, max-age=31536000, immutable`, 동적 경로는 Cache Rules로 BYPASS (`/api/*`, 로그인 등). ([Cloudflare Docs][8])

---

## 3) 백엔드 배포 — Cloud Run

* **런타임:** FastAPI + Uvicorn, Artifact Registry 이미지 → Cloud Run 서비스. ([Google Cloud][2])
* **트래픽 관리:** 리비전별 트래픽 스플릿(Blue/Green/Canary) 및 즉시 롤백. ([Google Cloud][9])
* **DB 연결:** Cloud SQL 커넥터/프록시, IAM 인증. ([Google Cloud][3])
* **비밀:** Secret Manager → Cloud Run 환경변수/파일 주입. ([Google Cloud][10])
* **헬스 프로브:** Cloud Run은 `/healthz`(liveness)와 `/readyz`(readiness)를 사용하며, `/readyz`는 DB·Redis 핑이 성공해야 200을 반환한다. 배포 전 `pytest mbti-arcade/tests/test_health.py -q`와 `docker compose logs mbti-arcade | grep readyz`로 상태를 캡처한다.
* **배포 예:** `gcloud run deploy api --image $IMAGE_URL --region asia-northeast3 --allow-unauthenticated` → 트래픽 점진 전환. ([Google Cloud][11])

---

## 4) 네트워킹·보안 — Cloudflare + GCP

* **TLS:** Cloudflare Universal SSL, 필요 시 오리진 인증서로 종단간 암호화. ([Cloudflare Docs][12])
* **WAF/봇 차단:** Rate Limiting Rules, Bot Fight Mode, Turnstile(선택). ([Cloudflare Docs][13]) ([Cloudflare Docs][14])
* **캐시 제어:** Cache Rules로 API BYPASS, 쿠키 조건. ([Cloudflare Docs][8])
* **검색 제어:** 결과/공유 URL `noindex` 메타 또는 `X-Robots-Tag`. ([Google for Developers][15])

---

## 5) CI/CD — GitHub Actions

**FE (Pages)**

```yaml
name: fe-deploy
on: { push: { branches: [main], paths: ["fe/**"] } }
jobs:
  build_deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: cd fe && npm ci && npm run build
      - name: Publish to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CF_API_TOKEN }}
          accountId: ${{ secrets.CF_ACCOUNT_ID }}
          projectName: 360me-app
          directory: fe/dist
```

**BE (Cloud Run)**

```yaml
name: be-deploy
on: { push: { branches: [main], paths: ["be/**"] } }
jobs:
  build_push_deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/setup-gcloud@v2
        with:
          project_id: ${{ secrets.GCP_PROJECT }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}
      - name: Build & Push
        run: |
          gcloud auth configure-docker ${{ secrets.GAR_HOST }} -q
          docker build -t ${{ secrets.GAR_HOST }}/${{ secrets.GCP_PROJECT }}/api:${{ github.sha }} be
          docker push ${{ secrets.GAR_HOST }}/${{ secrets.GCP_PROJECT }}/api:${{ github.sha }}
      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v2
        with:
          service: "api"
          image: "${{ secrets.GAR_HOST }}/${{ secrets.GCP_PROJECT }}/api:${{ github.sha }}"
          region: "asia-northeast3"
          flags: "--allow-unauthenticated"
```

대규모 파이프라인 변경/새 매니지드 서비스 도입은 Ask 게이트로 분류합니다.

---

## 6) 비밀/설정 관리

* Secret Manager 버전을 Cloud Run 서비스 계정이 참조, 주입 후 감사 로그 모니터링. ([Google Cloud][10])
* 변경 주기·회전 계획, 참조 실패 시 리비전 롤백. Medium 사례 참고. ([Medium][17])

---

## 7) 관측성/로깅

* OpenTelemetry FastAPI 자동계측 → GCP Logging/Trace로 전송. ([opentelemetry-python-contrib.readthedocs.io][18])
* 릴리즈별 대시보드: P95, 에러율, GapScore 계산 상태, Web Vitals 수집.

---

## 8) 광고·SEO·공유

* `ads.txt` 루트 배치, 퍼블리셔 ID 기록. ([Google Help][19])
* OG 이미지: Cloud Run API에서 Satori/Sharp로 생성 → Cloudflare 캐시/만료. ([Cloudflare Docs][8])
* 결과/공유 페이지 `noindex`/`X-Robots-Tag`. ([Google for Developers][15])

---

## 9) 롤아웃 전략

* Cloud Run 리비전 트래픽 스플릿으로 10%→50%→100% 전환. 문제 시 이전 리비전으로 즉시 롤백. ([Google Cloud][9])
* 릴리즈 체크리스트: E2E 시나리오, Web Vitals(75p), RFC 9457 오류 스냅샷, k≥3 검증, AdSense 정책.

---

## 10) 비용/성능 가드레일

* Cloud Run `min-instances=0`로 시작, 트래픽 증가 시 1 이상. 동시성 조정. ([Google Cloud][2])
* Cloudflare 캐시로 오리진 부하 절감, API는 BYPASS. ([Cloudflare Docs][20])
* 리전은 사용자의 지연을 최소화하도록 서울 우선.

---

## 11) 운영 정책

* Rate Limit / Managed Challenge를 `/api/other/submit` 등 민감 엔드포인트에 적용. ([Cloudflare Docs][13])
* `X-Robots-Tag: noindex, nofollow` 헤더, HTML `robots` 메타 병행. ([Google for Developers][15])
* SSL 상태 모니터링(Cloudflare 인증서 만료 확인). ([Cloudflare Docs][12])

---

## 12) 단계별 타임라인

1. **W1:** Cloudflare Pages 도메인 연결, Cloud Run 샘플 컨테이너, Cloud SQL 연결 PoC. ([Cloudflare Docs][1])
2. **W2:** GitHub Actions CI/CD, Secret Manager 연동, 베타 도메인 오픈. ([GitHub][16])
3. **W3:** Cloudflare WAF/RateLimit/Cache Rules, OTel 대시보드. ([Cloudflare Docs][13])
4. **W4:** Canary → GA 전환, 롤백 리허설. ([Google Cloud][9])

---

## 13) 리스크와 완화

* **캐시 오탑재:** 리비전 해시 및 캐시 무효화 계획 유지.
* **봇 트래픽 급증:** RateLimit 상향, Managed Challenge 활성화. ([Cloudflare Docs][21])
* **DB 마이그:** Ask 게이트; 사전 백업·롤백 스크립트 필수.

---

## 14) 운영 체크리스트

* [ ] Pages 배포 + 커스텀 도메인 + SSL 확인. ([Cloudflare Docs][5])
* [ ] Cloud Run 리비전 헬스, 트래픽 10% 카나리. ([Google Cloud][9])
* [ ] Cloud SQL 연결/백업 설정. ([Google Cloud][3])
* [ ] Secret Manager 참조/권한 테스트. ([Google Cloud][10])
* [ ] OTel 대시보드 준비. ([opentelemetry-python-contrib.readthedocs.io][18])
* [ ] WAF/RateLimit 룰 검증. ([Cloudflare Docs][13])
* [ ] `noindex`/`X-Robots-Tag` 적용. ([Google for Developers][15])
* [ ] `ads.txt` 검증. ([Google Help][19])

---

## 참고 링크

[1]: https://developers.cloudflare.com/pages/framework-guides/deploy-a-react-site/?utm_source=chatgpt.com
[2]: https://cloud.google.com/run/docs/deploying?utm_source=chatgpt.com
[3]: https://cloud.google.com/sql/docs/postgres/connect-run?utm_source=chatgpt.com
[4]: https://cloud.google.com/run/docs/locations?utm_source=chatgpt.com
[5]: https://developers.cloudflare.com/pages/configuration/custom-domains/?utm_source=chatgpt.com
[6]: https://vite.dev/guide/static-deploy?utm_source=chatgpt.com
[7]: https://developers.cloudflare.com/pages/framework-guides/deploy-a-vite3-project/?utm_source=chatgpt.com
[8]: https://developers.cloudflare.com/cache/how-to/cache-rules/?utm_source=chatgpt.com
[9]: https://cloud.google.com/run/docs/rollouts-rollbacks-traffic-migration?utm_source=chatgpt.com
[10]: https://cloud.google.com/run/docs/configuring/services/secrets?utm_source=chatgpt.com
[11]: https://cloud.google.com/run/docs/quickstarts/deploy-container?utm_source=chatgpt.com
[12]: https://developers.cloudflare.com/ssl/?utm_source=chatgpt.com
[13]: https://developers.cloudflare.com/waf/rate-limiting-rules/?utm_source=chatgpt.com
[14]: https://developers.cloudflare.com/bots/get-started/bot-fight-mode/?utm_source=chatgpt.com
[15]: https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag?utm_source=chatgpt.com
[16]: https://github.com/google-github-actions/deploy-cloudrun?utm_source=chatgpt.com
[17]: https://medium.com/google-cloud/cloud-run-hot-reload-your-secret-manager-secrets-ff2c502df666?utm_source=chatgpt.com
[18]: https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html?utm_source=chatgpt.com
[19]: https://support.google.com/adsense/answer/12171612?hl=en&utm_source=chatgpt.com
[20]: https://developers.cloudflare.com/cache/?utm_source=chatgpt.com
[21]: https://developers.cloudflare.com/waf/rate-limiting-rules/best-practices/?utm_source=chatgpt.com
