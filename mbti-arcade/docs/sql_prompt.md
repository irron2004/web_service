**요약(3–5줄)**
DB 질의 생성/검증용 **프롬프트·체크리스트** 템플릿입니다. 스키마 요약·제약·엣지 케이스·성능 주의·검증 쿼리 패턴을 포함하며, 변경 전후 **무결성·카운트 검증**을 강제합니다.

```yaml
---
version: "1.0"
date: "2025-09-16"
domains: ["backend"]
owner: "이지율"
source_of_truth: "mbti-arcade/docs/sql_prompt.md"
use_browsing: false
---
```

### 핵심 체크리스트(발췌)

* 스키마 요약: `users(id, email unique, ...)`, `sessions(id, owner_id fk, ...)`, `responses(id, session_id fk, ...)`
* 제약: 고유/널/체크/외래키, 타임존·소프트삭제·익명 처리
* 성능: 인덱스·키셋 페이지네이션, `EXPLAIN ANALYZE`
* 검증 쿼리: 변경 전후 rowcount·FK 일관성·에러 로그 점검

---
