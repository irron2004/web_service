**요약(3–5줄)**
React Router + TanStack Query + Zustand 조합을 기본으로 하고, 서버 상태는 Query, 로컬 상태는 Zustand로 관리합니다. UI는 **Chart.js 레이더/스캐터**, 에러바운더리, 스켈레톤을 갖추며, **WCAG 2.2 AA**와 **Web Vitals** 성능 버짓을 준수합니다. 공유 품질을 위해 OG 메타 태그 표준을 적용합니다.

```yaml
---
version: "1.0"
date: "2025-09-17"
owner: "FE 리드"
domains: ["frontend"]
source_of_truth: "mbti-arcade/docs/frontend_style.md"
use_browsing: true
---
```

### 아키텍처

* 라우팅: React Router. ([React Router Docs][1])
* 서버 상태: TanStack Query, 로컬 상태: Zustand. ([TanStack][2])
* 빌드: Vite, 코드 스플리팅과 동적 import 활용.

### UI 품질/보안

* 에러바운더리·재시도, 스켈레톤/로딩 완화.
* WCAG 2.2 AA, 키보드 내비게이션, APG 패턴. ([W3C][3])
* CSP/DOM Sanitization, 환경 변수 시크릿 노출 금지.

### 성능 & 공유

* 성능 버짓: **LCP≤2.5s / INP≤200ms / CLS≤0.1 (@75p)**. ([web.dev][4])
* OG 태그: `og:title`, `og:description`, `og:image(1200×630)`, `og:url`. ([ogp.me][5])
* 차트: Chart.js 레이더/스캐터, 모바일 최적화. ([chartjs.org][6])

---

## 참고 문헌

[1]: https://reactrouter.com/ "React Router Official Documentation"  
[2]: https://tanstack.com/query/latest/docs/framework/react/overview "TanStack Query React Docs"  
[3]: https://www.w3.org/TR/WCAG22/ "Web Content Accessibility Guidelines (WCAG) 2.2"  
[4]: https://web.dev/articles/vitals "Web Vitals | Articles"  
[5]: https://ogp.me/ "The Open Graph protocol"  
[6]: https://www.chartjs.org/docs/latest/charts/radar.html "Radar Chart"
