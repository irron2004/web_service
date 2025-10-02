from app.utils.privacy import NOINDEX_VALUE
from app.data.questions import questions_for_mode


def _extract_dimensions(png_bytes: bytes) -> tuple[int, int]:
    # PNG header: 8 bytes signature, 4 bytes chunk length, 4 bytes chunk type, then width/height
    width = int.from_bytes(png_bytes[16:20], "big")
    height = int.from_bytes(png_bytes[20:24], "big")
    return width, height


def _create_session(client, mode: str = "basic") -> dict:
    response = client.post("/api/sessions", json={"mode": mode})
    assert response.status_code == 201
    return response.json()


def _answers(mode: str):
    return [{"question_id": q["id"], "value": 3} for q in questions_for_mode(mode)]


def _submit_self(client, session_id: str, mode: str = "basic") -> None:
    response = client.post(
        "/api/self/submit",
        json={"session_id": session_id, "answers": _answers(mode)},
    )
    assert response.status_code == 200


def _submit_other(client, token: str, relation: str = "friend") -> None:
    payload = {
        "invite_token": token,
        "relation_tag": relation,
        "answers": _answers("basic"),
    }
    response = client.post("/api/other/submit", json=payload)
    assert response.status_code in {201, 200}


def test_og_image_returns_png_locked_state(client):
    session = _create_session(client)
    _submit_self(client, session["session_id"])

    response = client.get(f"/share/og/{session['invite_token']}.png")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
    assert response.headers["X-Robots-Tag"] == NOINDEX_VALUE
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(response.content) > 2000
    assert response.headers["Cache-Control"] == "public, max-age=600"
    width, height = _extract_dimensions(response.content)
    assert (width, height) == (1200, 630)


def test_og_image_after_unlock_includes_headers(client):
    session = _create_session(client)
    _submit_self(client, session["session_id"])

    for suffix in range(3):
        client.post(
            "/api/other/submit",
            json={
                "invite_token": session["invite_token"],
                "relation_tag": "friend",
                "rater_key": f"r{suffix}",
                "answers": _answers("basic"),
            },
        )

    response = client.get(f"/share/og/{session['invite_token']}.png")
    assert response.status_code == 200
    assert "ETag" in response.headers
    assert response.headers["Cache-Control"].startswith("public")
    width, height = _extract_dimensions(response.content)
    assert (width, height) == (1200, 630)
