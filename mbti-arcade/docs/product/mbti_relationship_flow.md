# MBTI 결과 공유 플로우 스펙

## 1) 변경 요약(한 줄)

**“친구 평가하기” → “친구/동료/가족에게 공유하기”**로 변경하고, 링크 수신자는 **관계 선택 + 제3자 평가**를 수행 → 제출 즉시 **1:1 비교 요약(개인 미리보기)** 를 보고, 피평가자는 응답 **3명 이상(k≥3)** 모이면 **관계별 집계 비교 리포트**와 **커뮤니케이션 가이드**를 확인.

---

## 2) 화면·카피(디자이너/프론트에 바로 전달)

### A. MBTI 결과 화면(피평가자)

* **헤더**: “나의 MBTI 결과”
* **핵심 CTA(변경)**: **[친구/동료/가족에게 공유하기]**
  * 서브: “관계별로 나를 어떻게 보는지 익명으로 확인해요 (1분)”
* **공유 모달**
  * 버튼: [링크 복사] [카카오톡] [QR] (채널 선택은 현 인프라에 맞춰 1~2종부터)
  * 안내: “링크를 받은 사람은 **관계**를 고르고, **당신을 기준으로 제3자 평가**를 진행합니다.”

### B. 초대 랜딩(`/i/{token}`; 수신자용)

* 상단: 아바타 + “**{표시명}** 님에 대한 인식 체크”
* **관계 선택 라디오**: 친구 / 동료 / 가족 / 배우자 / 기타
* **표시명(선택)**: (미입력 시 ‘익명’)
* **CTA**: [시작하기]
* 푸터: “제출 즉시 **1:1 비교 요약**을 볼 수 있고, {표시명}님은 응답 3명 이상 모이면 **관계별 리포트**를 확인합니다.”

### C. 제3자 평가(Other 32문항)

* 진행바 “8/32”, [이전] [다음]
* 제출 후 → **개인 미리보기(수신자 전용 요약)**

### D. 개인 미리보기(수신자 전용, 1:1)

* 타이틀: “내가 본 {표시명}님 vs 본인이 생각한 자신”
* 뱃지: **Self: ESTJ** / **Your view: ISTP** (예시)
* **축 차이(E/I, S/N, T/F, J/P)**: 아이콘 + 간단 설명
* CTA: “{표시명}님의 관계별 리포트는 응답 3명 이상 모이면 열립니다.”

### E. 피평가자 리포트(집계; k≥3)

* 요약: “관계별 인식 지도”, 응답자 수, PGI(인지 격차 지수)
* 카드(관계별): **Top 유형/비율**, **합의도**, **Self↔Top 차이 축**
* **커뮤니케이션 가이드**(축별 팁; 아래 5절 참고)
* 공유 영역: OG 카드 + “나도 받아보기 링크”

> **공개 화면 개발용어 금지**: RFC, X‑Request‑ID, DB 등 기술 문구는 미노출(내부 문서로 이동).

---

## 3) 사용자 플로우(간단 다이어그램)

```
[본인(Self) MBTI 결과]
       └─▶ [공유하기] → /i/{token}
                        └─ 수신자: 관계 선택 + 표시명(옵션)
                            └─ 32문항 평가 → 제출
                                 ├─ (수신자) 개인 미리보기(1:1 요약)
                                 └─ (본인) 대시보드 응답 수 증가
                                       └─ n≥3 → 리포트 해금(관계별 집계)
```

---

## 4) 데이터/API/스키마 변경(개발자용)

### 4.1 API(요약)

* `POST /v1/self/mbti` → { session_id, self_mbti: "ESTJ" } (직접입력/검사 결과 저장)
* `POST /v1/invites` → { session_id } → { token }
* `GET /i/{token}` → 표시명/아바타/MBTI 일부(옵션) 렌더
* `POST /v1/participants/{token}` → { relation, display_name?, consent_display }
* `POST /v1/answers/{participant_id}` → { answers[] } → 204
* `POST /v1/compute/participant/{participant_id}/type` → { perceived_type: "ISTP", axes:{EI:-0.4,...} }
  * 또는 서버에서 `answers` 저장 시 **동시에 산출**하여 participants에 캐싱
* `GET /v1/report/participant/{participant_id}` *(수신자 전용 1:1 미리보기)*
  → { self_type, your_view_type, diff_axes[], short_tips[] }
* `GET /v1/report/session/{session_id}` *(집계; k≥3)*
  → 관계별 Top/분포/합의도/PGI + 축별 가이드 텍스트

### 4.2 스키마(필드 추가)

* `sessions(self_mbti char(4), snapshot_owner_name text, snapshot_owner_avatar text)`
* `participants(relation enum, display_name_opt text, consent_display bool, perceived_type char(4), ei_sn_tf_jp jsonb)`
  *perceived_type/축점수는 제출 시 계산해 저장(조회 성능 향상)*
* `aggregate_rel(session_id, relation, n, top1_type, pct1, top2_type, pct2, confidence, pgi, updated_at)`

---

## 5) 점수/비교·가이드 로직(규칙 기반; LLM 선택적)

### 5.1 제3자 평가 → 유형 산출

* 각 문항 1~5점 → `d = v-3`(−2..+2), 문항 부호(sign)로 **EI/SN/TF/JP** 누적
* 각 축 `score_dim = Σ(sign_q * d_q)` → 0 기준으로 앞/뒤 문자 결정
* **유형** = 4축 문자 조합(유효 16가지로만 매핑; “ISTF” 같은 비표준 조합 방지)
* **정규화** `norm = score_dim / (2 * n_dim_q)` (−1..+1), 차트에 사용

### 5.2 Self vs Others 비교

* 수신자 미리보기(1:1): `self_type` vs `your_view_type` + `diff_axes` 리스트
* 집계(k≥3): 관계별 분포 → **Top 유형/합의도(conf)** 산출
* **PGI**(인지 격차 지수; 0~100): `25 * Hamming(Self, Top_r) * (0.5+0.5*conf)`
  * Hamming: 축 문자 차이 개수(0~4)

### 5.3 축별 커뮤니케이션 가이드(예시)

* **E vs I**
  * **잠재 이슈**: 대화 빈도/속도 기대치 불일치(즉각 대화 vs 정리 후 응답)
  * **해결 팁**: “**체크‑인 약속**(하루 1회/5분)” + “**말할 차례** 규칙”
* **S vs N**
  * **잠재 이슈**: **세부 vs 큰그림** 충돌
  * **해결 팁**: 안건마다 “**요약 1줄 → 근거 3줄**”로 레벨 맞추기
* **T vs F**
  * **잠재 이슈**: **논리 vs 감정** 순서 다름
  * **해결 팁**: “**감정 확인 1문장 → 논의**” 2단계 스크립트
* **J vs P**
  * **잠재 이슈**: **계획 고정 vs 유연/즉흥**
  * **해결 팁**: **앵커 3개(반드시) + 자유 슬롯 2개(선택)**로 일정 합의

> *이 블록은 규칙 기반으로도 충분히 생성 가능(LLM은 톤 다듬기 옵션).* 

---

## 6) 수락 기준(DoD) & 테스트 골격

### 6.1 수락 기준(요약)

1. **MBTI 결과 CTA 변경**: “친구/동료/가족에게 공유하기” 노출
2. **수신자 플로우**: 관계 선택 → 평가 제출 → **개인 미리보기** 표시
3. **집계 리포트**: 응답 k≥3 시 관계별 Top/합의도/PGI/가이드 노출, k<3 잠금
4. **개발 용어 미노출**: 공개 화면에서 RFC/DB 등 문구 0건
5. **링크/리다이렉트**: 모두 `url_for` + CANONICAL_BASE_URL 기반, 400/Invalid Host 없음

### 6.2 테스트 골격(발췌)

```python
from app.scoring import compute_type

def test_compute_type_valid():
    t, axes = compute_type(answers=FAKE_ANSWERS)  # 32문항
    assert t in {"INTJ","INTP","ENTJ","ENTP","INFJ","INFP","ENFJ","ENFP",
                 "ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"}
    # ISTF 같은 비표준 유형은 절대 나오지 않아야 함
```

```python
def test_participant_preview(client, seed_session_with_self_mbti):
    p = client.post(f"/v1/participants/{seed_session_with_self_mbti.token}",
                    json={"relation":"coworker"}).json()
    client.post(f"/v1/answers/{p['participant_id']}", json={"answers":FAKE_ANSWERS})
    r = client.get(f"/v1/report/participant/{p['participant_id']}")
    body = r.json()
    assert body["self_type"] and body["your_view_type"]
    assert "diff_axes" in body and isinstance(body["diff_axes"], list)
```

```python
def test_aggregate_unlock(client, seed_session_three_participants):
    r = client.get(f"/v1/report/session/{seed_session_three_participants.id}")
    b = r.json()
    assert b["unlocked"] is True
    assert b["relations"][0]["top1_type"]
    assert "pgi" in b
```

```ts
test('Self 결과→공유→수신자 3명→집계 해금', async ({ page, context }) => {
  await page.goto('/mbti/result');
  await page.getByRole('button', { name: '친구/동료/가족에게 공유하기' }).click();
  const inviteUrl = await page.locator('#invite-url').textContent();

  for (const rel of ['friend','coworker','family']) {
    const p = await context.newPage();
    await p.goto(inviteUrl!);
    await p.getByLabel('관계').selectOption(rel);
    await p.getByRole('button', { name: '시작하기' }).click();
    // (문항 자동채우기 헬퍼)
    await p.getByRole('button', { name: '제출' }).click();
    await p.getByText('1:1 비교 요약').isVisible();
    await p.close();
  }
  await page.goto(inviteUrl!.replace('/i/','/result/'));
  await page.getByText('관계별 인식 지도').isVisible();
});
```

```python
DEV_WORDS = ["RFC", "X-Request-ID", "database", "SQL", "rate limit", "OTel"]
def test_public_pages_have_no_dev_terms(httpx_client):
    for path in ["/","/i/sample","/mbti/result"]:
        html = httpx_client.get(path).text
        assert not any(w.lower() in html.lower() for w in DEV_WORDS)
```

---

## 7) 티켓(추가/변경 포인트만)

* **TKT‑A01** 결과 CTA 텍스트/동작 변경: “친구/동료/가족에게 공유하기”
  *AC*: 결과 화면에 새 CTA 노출, 공유 모달에서 링크 복사/QR 제공
* **TKT‑A02** 초대 랜딩 관계 선택 + 표시명(옵션) + 시작
  *AC*: 관계 미선택 시 검증 오류, 익명 가능
* **TKT‑A03** 제출 후 **수신자 개인 미리보기** API/화면
  *AC*: self_type vs your_view_type + diff_axes + 축별 1문장 팁
* **TKT‑A04** 집계 리포트에 축별 가이드 텍스트 삽입
  *AC*: 관계별 카드에 Top/합의도/PGI/가이드 문구 노출
* **TKT‑A05** 스키마 확장: sessions.self_mbti, participants.perceived_type/axes
  *AC*: 저장/조회 경로 테스트 통과

---

## 8) 운영/정책(변경 없음, 재확인)

* **k≥3 공개 정책** 계속 유지(집계 리포트 잠금/해금)
* **PII 최소수집**: 이메일/전화 **수집 안 함**, 표시명만(선택)
* 도메인 **A안 유지**: Railway 주소를 CANONICAL_BASE_URL로 사용, 모든 초대/공유 링크가 이 도메인으로 생성

---

## 9) 샘플 리포트 문구(사용자에게 보일 톤)

> **한눈 요약**
> 본인은 **ESTJ**, 당신은 **ISTP**로 보았네요. **E↔I, S↔N, J↔P** 축에서 차이가 커요.
>
> **가능한 오해**
> 빠른 결정과 일정 고정(ESTJ)이, 상대 눈에는 “여유 없이 밀어붙이는 느낌”으로 비칠 수 있어요(ISTP 관점).
>
> **대화 팁(이번 주 실험)**
>
> 1. 회의 시작 전에 **요약 1줄 + 선택지 2개** 제시(큰그림/세부 균형)
> 2. 결정 전 **의견 모으는 3분 타임**(I/P에게 준비 시간 제공)
> 3. 주간 계획은 **앵커 3개 + 자유 슬롯 2개**로 합의

---

### 정리

* 버튼 문구/플로우를 공유 중심으로 바꾸고, **관계 선택→제3자 평가** → **1:1 미리보기** → **k≥3 집계 리포트**로 이어지게 만들면, **사용자 의도(“다른 사람 눈에 나는 어떤가”)**를 정확히 충족합니다.
* 위 스펙/카피/테스트 골격 그대로 구현하면 팀 간 커뮤니케이션 비용을 줄이고, 출시 후 **바이럴 루프**도 자연스럽게 동작합니다.
