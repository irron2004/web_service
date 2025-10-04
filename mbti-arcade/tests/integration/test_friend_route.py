from http import HTTPStatus


def test_friend_route_ok(client):
    response = client.get("/mbti/friend", headers={"host": "testserver"})
    assert response.status_code == HTTPStatus.OK
    assert "친구 MBTI 평가" in response.text


def test_untrusted_host_rejected(client):
    response = client.get("http://bad.example.com/mbti/friend")
    assert response.status_code in {HTTPStatus.BAD_REQUEST, HTTPStatus.MISDIRECTED_REQUEST}
    body = response.json()
    assert body["type"].startswith("https://")
    assert body["status"] == response.status_code
