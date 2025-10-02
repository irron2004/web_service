from app.core.config import REQUEST_ID_HEADER
def test_request_id_generated_when_missing(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    request_id = response.headers.get(REQUEST_ID_HEADER)
    assert request_id

def test_request_id_preserved_when_provided(client):
    provided = "req-12345"
    response = client.get("/healthz", headers={REQUEST_ID_HEADER: provided})
    assert response.status_code == 200
    assert response.headers.get(REQUEST_ID_HEADER) == provided
