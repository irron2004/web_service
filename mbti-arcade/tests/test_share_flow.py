from urllib.parse import parse_qs, urlparse


def test_share_flow(client):
    """공유 링크 생성 → 퀴즈 → 결과 플로우 테스트"""
    
    # 1. 공유 링크 생성
    share_data = {
        "name": "테스트 사용자",
        "email": "test@example.com",
        "my_mbti": "INTJ"
    }
    
    response = client.post("/share", data=share_data, follow_redirects=False)
    assert response.status_code == 303  # Redirect
    
    # 2. 퀴즈 페이지 접근 (리다이렉트 URL에서 토큰 추출)
    # 리다이렉트 URL에서 토큰을 추출
    redirect_url = response.headers.get("location")
    assert redirect_url is not None
    assert "/mbti/share_success?url=" in redirect_url
    
    # URL에서 토큰 추출
    parsed_url = urlparse(redirect_url)
    query_params = parse_qs(parsed_url.query)
    share_url = query_params.get("url", [None])[0]
    assert share_url is not None
    assert "/quiz/" in share_url
    test_token = share_url.split("/quiz/")[1]
    
    response = client.get(f"/quiz/{test_token}")
    assert response.status_code == 200
    
    # 3. 퀴즈 제출
    quiz_data = {
        "token": test_token,
        "relation": "friend"
    }
    
    # 24개 질문에 대한 답변 추가 (실제 데이터베이스 질문 ID 사용)
    question_ids = [1, 2, 101, 102, 201, 202, 3, 4, 103, 104, 203, 204, 5, 6, 105, 106, 205, 206, 301, 302, 401, 402, 501, 502]
    for qid in question_ids:
        quiz_data[f"q{qid}"] = "3"  # 보통이다
    
    response = client.post(f"/mbti/result/{test_token}", data=quiz_data)
    assert response.status_code == 200

def test_expired_token(client):
    """만료된 토큰 테스트"""
    
    # 잘못된 토큰으로 접근
    response = client.get("/quiz/invalid_token")
    assert response.status_code == 403

def test_rate_limit_returns_problem_details(client):
    """Rate limiting 테스트"""

    share_data = {
        "name": "테스트 사용자",
        "email": "test@example.com",
        "my_mbti": "INTJ",
    }

    first = client.post("/share", data=share_data, follow_redirects=False)
    assert first.status_code == 303

    limited = client.post("/share", data=share_data, follow_redirects=False)
    assert limited.status_code == 429

    body = limited.json()
    assert body["type"].endswith("/rate-limit")
    assert body["title"] == "Rate Limit Exceeded"
    assert "Retry-After" in limited.headers
