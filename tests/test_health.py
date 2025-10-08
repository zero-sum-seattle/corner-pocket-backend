from fastapi.testclient import TestClient
from corner_pocket_backend.main import corner_pocket_backend


def test_health():
    c = TestClient(corner_pocket_backend)
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True
