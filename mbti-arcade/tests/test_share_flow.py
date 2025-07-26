import pytest
import httpx
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_share_flow():
    """공유 링크 생성 → 퀴즈 → 결과 플로우 테스트"""
    
    # 1. 공유 링크 생성
    share_data = {
        "name": "테스트 사용자",
        "email": "test@example.com",
        "my_mbti": "INTJ"
    }
    
    response = client.post("/share", data=share_data)
    assert response.status_code == 303  # Redirect
    
    # 2. 퀴즈 페이지 접근 (토큰 추출)
    # 실제로는 share_success 페이지에서 토큰을 추출해야 함
    # 여기서는 간단한 테스트를 위해 토큰을 직접 생성
    from app.core.token import issue_token
    test_token = issue_token("test_pair_id", "INTJ")
    
    response = client.get(f"/quiz/{test_token}")
    assert response.status_code == 200
    
    # 3. 퀴즈 제출
    quiz_data = {
        "token": test_token,
        "relation": "friend"
    }
    
    # 24개 질문에 대한 답변 추가
    for i in range(1, 25):
        quiz_data[f"q{i}"] = "3"  # 보통이다
    
    response = client.post(f"/mbti/result/{test_token}", data=quiz_data)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_expired_token():
    """만료된 토큰 테스트"""
    
    # 잘못된 토큰으로 접근
    response = client.get("/quiz/invalid_token")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_rate_limit():
    """Rate limiting 테스트"""
    
    share_data = {
        "name": "테스트 사용자",
        "email": "test@example.com",
        "my_mbti": "INTJ"
    }
    
    # 연속으로 여러 번 요청
    for _ in range(3):
        response = client.post("/share", data=share_data)
    
    # Rate limit에 걸려야 함
    assert response.status_code == 429

if __name__ == "__main__":
    pytest.main([__file__]) 