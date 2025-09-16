**요약(3–5줄)**
React는 **React Router**로 라우팅하고, 서버상태는 **TanStack Query**, 로컬상태는 **Zustand**를 사용합니다. **에러바운더리/스켈레톤**, **APG 패턴**, **CSP/XSS 방어**를 기본으로 하며, **Web Vitals(LCP/INP/CLS)**를 성능 버짓으로 채택합니다. ([React Router][14])

```yaml
---
version: "1.0"
date: "2025-09-16"
domains: ["react"]
owner: "이지율"
source_of_truth: "docs/frontend_style.md"
use_browsing: true
---
```

### 아키텍처

* **Routing:** React Router. ([React Router][14])
* **서버상태:** TanStack Query(캐싱/동기화), 로컬: Zustand. ([TanStack][13])
* **빌드:** Vite(코드 스플리팅/동적 임포트).

### UI 품질/보안

* 에러바운더리·재시도, 스켈레톤·로딩 지연 완화.
* WCAG 2.2 AA/APG 패턴, 키보드 내비게이션. ([W3C][6])
* CSP 엄격, DOM Sanitization, 환경변수 시크릿 주입 금지.

### 성능 버짓 & 측정

* **LCP≤2.5s / INP≤200ms / CLS≤0.1 (@75p)**, Lighthouse + RUM/CrUX. ([web.dev][3])

---
