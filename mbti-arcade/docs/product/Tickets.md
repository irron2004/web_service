---
version: "1.0"
date: "2025-10-04"
project: "If I were you – 프로필·초대·참여 인테이크 정비"
owner: "PM · 이지율"
principles: ["한 작업=한 PR", "RFC9457 오류 표준", "X-Request-ID/OTel", "k≥3 공개", "noindex"]
environments: ["dev","stg","prod"]
---

🔴 P0 — 기능 중단/신뢰 저하 즉시 해결

---

TKT‑001 /mbti/friend 500(Invalid URL) 원인 제거 & 라우팅 정비

요약
/mbti/friend 진입 시 500이 발생하는 이슈를 제거한다. 초대·공유 URL 생성 로직을 문자열 치환 → 프레임워크 URL 역참조 방식으로 교체하고, 비신뢰 Host 헤더는 거부한다.

수락 기준

GET /mbti/friend 200 응답(레이아웃 렌더)

공유/리다이렉트 시 url_for(또는 request.url_for) 기반으로 절대/상대 URL 생성

비신뢰 Host로 요청 시 400(Bad Request)

잘못된 토큰/경로는 RFC9457 포맷 오류 응답


테스트 코드 골격

# tests/unit/test_url_builder.py
from app.urling import build_invite_url


def test_build_invite_url_uses_url_for(mock_request):
    url = build_invite_url(mock_request, token="abc")
    assert "/i/abc" in str(url)


# tests/integration/test_friend_route.py
def test_friend_route_ok(client):
    r = client.get("/mbti/friend", headers={"host": "testserver"})
    assert r.status_code == 200


def test_untrusted_host_rejected(client):
    r = client.get("/mbti/friend", headers={"host": "bad.example.com"})
    assert r.status_code in (400, 421)


# tests/integration/test_share_redirect.py
def test_share_redirect_is_valid_url(client):
    r = client.post("/mbti/share", json={"token": "abc"})
    assert r.status_code in (200, 302)
    loc = r.headers.get("location", "")
    assert loc and "://" not in loc or loc.startswith("https://")


# app/urling.py (스켈레톤)
from fastapi import Request


def build_invite_url(request: Request, token: str) -> str:
    # TODO: 필요 시 canonical_base_url 환경변수로 스킴 고정
    return request.url_for("invite_public", token=token)


---

TKT‑002 소유자 프로필 인테이크(표시명/아바타/MBTI 입력·검사)

요약
표시명(필수·2–20자), 아바타(선택), MBTI(입력 or 자체검사) 수집 화면+API.

수락 기준

유효 입력 시 201, 저장된 값은 세션 생성 시 스냅샷으로 고정

잘못된 입력(길이/금칙어) 422 RFC9457

UI에서 “초대 페이지에 표시” 스위치 기본 ON


테스트 코드 골격

# tests/integration/test_profile_api.py
def test_create_profile_ok(client, user_token):
    r = client.post(
        "/v1/profile",
        json={
            "display_name": "은하수",
            "show_public": True,
            "mbti_source": "input",
            "mbti_value": "INFP",
        },
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert r.status_code == 201


def test_profile_validation_error(client, user_token):
    r = client.post(
        "/v1/profile",
        json={"display_name": "a", "mbti_source": "input"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert r.status_code == 422
    body = r.json()
    assert {"type", "title", "status", "detail"}.issubset(body.keys())


---

TKT‑003 초대 링크 발급(/i/{token}) + 만료/정원 + 서버 헤더 렌더

요약
서명 토큰으로 초대 링크를 발급하고, 초대 페이지 상단에 소유자 표시명/아바타를 서버 조회로 렌더. URL에는 PII 포함 금지.

수락 기준

POST /v1/invites → 201 {token, expires_at, max_raters}

GET /i/{token} → 200, HTML에 표시명/아바타 보임

만료/정원 초과 → 410/429 RFC9457


테스트 코드 골격


def test_invite_issue_and_render(client, user_token):
    rv = client.post(
        "/v1/invites",
        json={"expires_in_days": 7, "max_raters": 50},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    token = rv.json()["token"]
    r = client.get(f"/i/{token}")
    assert r.status_code == 200
    assert "X-Robots-Tag" in r.headers and "noindex" in r.headers["X-Robots-Tag"]


def test_invite_expired(client):
    r = client.get("/i/expiredtoken")
    assert r.status_code == 410
    assert r.json()["type"].endswith("/errors/gone")


---

TKT‑004 응답자 인테이크(관계 선택 + 표시명 선택·익명)

요약
응답자는 **관계(친구/가족/부부/직장/기타)**를 선택하고, **표시명(선택·익명)**을 입력.

수락 기준

표시명 미입력 시 “익명”으로 기록, UI에 “익명” 배지 표시

201 저장 후 문항 페이지로 이동

잘못된 관계 값은 422 RFC9457


테스트 코드 골격


def test_participant_intake_ok(client):
    t = "validtoken"
    r = client.post(
        f"/v1/participants/{t}",
        json={"relation": "friend", "display_name": None, "consent_display": False},
    )
    assert r.status_code == 201


def test_participant_invalid_relation(client):
    r = client.post("/v1/participants/xyz", json={"relation": "alien"})
    assert r.status_code == 422


---

TKT‑005 미리보기/결과 API 실데이터 연동 + 실패 시 페일세이프

요약
홈/결과 페이지의 “미리보기”가 실제 집계 데이터로 동작. 실패 시 스켈레톤→친절한 오류 카드+재시도 버튼.

수락 기준

/api/result/preview 200 (샘플/실데이터)

실패(5xx/네트워크) 시 UI가 재시도 제공, 콘솔 에러 미노출


테스트 코드 골격


def test_preview_ok(client):
    r = client.get("/api/result/preview")
    assert r.status_code == 200
    assert "radar" in r.json()


# FE E2E (Playwright)
# - 미리보기 섹션이 스켈레톤 후 차트 렌더
# - 장애 주입 시 '다시 시도' 버튼 노출


---

TKT‑006 페이지에서 개발적 내용 제거 + 사용자 카피 반영

요약
공개 화면에서 “RFC9457, X‑Request‑ID, noindex, DB, SQL, 레이트리밋” 등 개발 용어/내부 지표를 전부 제거하고, 기획 기능 설명으로 교체.

수락 기준

지정 페이지(랜딩/초대/응답/결과) 텍스트에서 개발 용어 0건(정규식 체크)

PageContentSpec.md의 카피와 1:1 일치(스냅샷 테스트)


테스트 코드 골격

# tests/functional/test_copy_clean.py
DEV_WORDS = ["RFC9457", "X-Request-ID", "noindex", "SQL", "rate limit", "OTel"]


def test_public_pages_no_dev_terms(httpx_client):
    for path in ["/", "/mbti/friend", "/i/sampletoken"]:
        html = httpx_client.get(path).text
        assert not any(w.lower() in html.lower() for w in DEV_WORDS)


---

TKT‑007 k≥3 공개/잠금 정책 집행

요약
관계/세션 n<3이면 상세 차트 잠금(회색 카드) + “응답 3명 달성 시 해금” 안내.

수락 기준

n=0~2 → 잠금, n≥3 → 해금

잠금 상태에서 URL 직접 접근해도 서버가 요약만 제공


테스트 코드 골격


def test_k_anonymity_lock(client, seed_two_raters):
    r = client.get("/api/result/session/abc")
    payload = r.json()
    assert payload["unlocked"] is False


def test_k_anonymity_unlock(client, seed_three_raters):
    r = client.get("/api/result/session/abc")
    assert r.json()["unlocked"] is True


---

TKT‑008 미구현 메뉴 비노출(/arcade 등)

요약
메뉴에서 미구현 라우트(404 유발) 제거 또는 feature flag로 가림.

수락 기준

네비게이션 클릭으로 404 페이지 유도 0건

스냅샷: 네비 목록에 arcade/stats 없음


테스트 코드 골격


def test_nav_has_no_unimplemented(client):
    html = client.get("/").text
    assert "arcade" not in html.lower()


---

🟠 P1 — 품질/보안/바이럴

---

TKT‑009 보안/SEO 헤더 확장: noindex + Cache-Control + CSP

요약
민감 페이지에 X-Robots-Tag: noindex, nofollow, Cache-Control: private, no-store, CSP(script-src 'self') 적용. OG 이미지엔 캐시 허용.

수락 기준

/i/{token}, 결과/미리보기 페이지 응답 헤더에 noindex+no-store+CSP 존재

OG 이미지 /share/og/{token}.png에는 Cache-Control: public, max-age=600


테스트 코드 골격


def test_sensitive_pages_headers(client):
    r = client.get("/i/abc")
    h = r.headers
    assert "noindex" in h.get("X-Robots-Tag", "").lower()
    assert "no-store" in h.get("Cache-Control", "").lower()
    assert "content-security-policy" in (k.lower() for k in h.keys())


def test_og_cache_header(client):
    r = client.get("/share/og/abc.png")
    assert "public" in r.headers.get("Cache-Control", "").lower()


---

TKT‑010 세션 스냅샷 필드 추가 + 결정 패킷(포렌식)

요약
리포트의 이름/아바타를 세션 생성 시 스냅샷으로 저장. 계산 결과/버전 해시를 decision_packet으로 봉인.

수락 기준

DB에 sessions.snapshot_owner_name/avatar 필드 존재, 리포트에서는 해당 값 사용(변경 영향 없음)

/v1/compute/{session} 호출 시 decision_packet 레코드 생성


마이그레이션/테스트 골격

# alembic revision --autogenerate

def upgrade():
    op.add_column("sessions", sa.Column("snapshot_owner_name", sa.Text(), nullable=True))
    op.add_column("sessions", sa.Column("snapshot_owner_avatar", sa.Text(), nullable=True))


# tests/integration/test_snapshot.py
def test_session_uses_snapshot_name(client, seed_session):
    r = client.get(f"/v1/result/{seed_session.token}")
    assert seed_session.snapshot_owner_name in r.text


---

TKT‑011 OG 이미지 템플릿(1200×630 / 1080×1920)

요약
Self/Top/n/PGI를 담은 OG 이미지 생성 API와 템플릿 2종.

수락 기준

GET /share/og/{token}.png?style=story|link 200, <200ms

동일 데이터 해시→동일 ETag


테스트 골격


def test_og_render_ok(client):
    r = client.get("/share/og/abc.png?style=link")
    assert r.status_code == 200
    assert "ETag" in r.headers


---

TKT‑012 관측성: X‑Request‑ID 전파 & 트레이스 조인

수락 기준

수신 요청에 X-Request-ID 없으면 발급 후 응답 헤더에 반영

앱 로그 라인에 request_id 키 존재, 트레이스와 조인 가능


테스트 골격


def test_request_id_roundtrip(client):
    r = client.get("/", headers={"X-Request-ID": "abc-123"})
    assert r.headers.get("X-Request-ID") == "abc-123"


---

TKT‑013 집계/PGI/합의도 계산 모듈 단위 테스트

수락 기준

단일 유형 n=10 → conf≈1, PGI=0

균등분포 → conf≈0, gap 축 표시는 0~4 범위


테스트 골격

from app.core_report import compute_relation_agg


def test_confidence_and_pgi():
    agg = compute_relation_agg("INFP", ["INFP"] * 10)
    assert agg["confidence"] > 0.95 and agg["pgi"] == 0.0


---

TKT‑014 공개 카피/도움말 정비(기능 설명만 노출)

수락 기준

모든 공개 페이지에서 “개발 용어/내부 기술 지표”가 0건

PageContentSpec.md와 문구 일치


테스트 골격: TKT‑006 테스트와 동일(경로 확장)


---

E2E(Playwright) 공통 시나리오 골격

// tests/e2e/flow.spec.ts
import { test, expect } from '@playwright/test';


test('소유자 인테이크 → 초대 → 응답자 참여 → n=3 해금', async ({ page, context, browser }) => {
  await page.goto('/');
  await page.getByRole('button', { name: '시작하기' }).click();
  await page.fill('input[name="display_name"]', '은하수');
  await page.selectOption('select[name="mbti_source"]', 'input');
  await page.fill('input[name="mbti_value"]', 'INFP');
  await page.getByRole('button', { name: '초대 만들기' }).click();

  const inviteUrl = await page.locator('#invite-url').textContent();

  // 3명의 응답자 시뮬레이션
  for (const who of ['친구1','친구2','친구3']) {
    const p = await context.newPage();
    await p.goto(inviteUrl!);
    await p.getByLabel('관계').selectOption('friend');
    await p.fill('input[name="participant_name"]', who);
    await p.getByRole('button', { name: '시작' }).click();
    // TODO: 문항 자동 선택 헬퍼
    await p.getByRole('button', { name: '제출' }).click();
    await p.close();
  }

  await page.goto(inviteUrl!.replace('/i/','/result/'));
  await expect(page.getByText('인사이트 해금')).toBeVisible();
  await expect(page.getByTestId('radar-chart')).toBeVisible();
});


---

마지막 확인(출고 게이트)

[ ] 모든 공개 페이지에서 개발적 용어 0건 (테스트 통과)

[ ] /mbti/friend 500 제거, 초대→응답 플로우 E2E 통과

[ ] k≥3 잠금/해금 정상 동작

[ ] 민감 페이지 noindex + no-store + CSP 헤더 적용

[ ] 세션 스냅샷 표시명으로 리포트 일관성 확보

[ ] OG 이미지 생성 API OK(캐시/ETag)


---

필요하시면, 위 테스트 골격을 실 프로젝트 경로/모듈명에 맞춰 바로 실행 가능한 PR 초안(라우터/DTO/템플릿 최소 구현 포함)으로도 작성해 드리겠습니다.

