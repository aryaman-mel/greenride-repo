from app import app

def test_index():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200

def test_health():
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"

def test_rides_returns_list():
    client = app.test_client()
    resp = client.get("/rides")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)
    assert len(resp.get_json()) > 0