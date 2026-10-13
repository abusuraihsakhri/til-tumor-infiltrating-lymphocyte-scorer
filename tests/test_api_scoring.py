"""API scoring and audit-log access regression tests."""
from fastapi.testclient import TestClient
from agents.api import app

client = TestClient(app)


def test_score_endpoint():
    response = client.post("/api/score", json={"stromal_area": 200, "til_area": 50})
    assert response.status_code == 200
    assert response.json()["stromal_til_percent"] == 25.0


def test_score_validates_bounds():
    for payload in (
        {"stromal_area": 0, "til_area": 0},
        {"stromal_area": 10, "til_area": 12},
        {"stromal_area": 10, "til_area": -1},
    ):
        assert client.post("/api/score", json=payload).status_code == 422


def test_static_app_available():
    response = client.get("/")
    assert response.status_code == 200
    assert "web/scorer.js" in response.text
    assert client.get("/web/scorer.js").status_code == 200


def test_audit_logs_disabled_without_token(monkeypatch):
    monkeypatch.delenv("AUDIT_LOGS_TOKEN", raising=False)
    assert client.get("/api/audit/logs").status_code == 403


def test_audit_logs_with_token(monkeypatch):
    monkeypatch.setenv("AUDIT_LOGS_TOKEN", "local-demo-secret")
    assert client.get("/api/audit/logs").status_code == 403
    assert client.get("/api/audit/logs", headers={"X-Audit-Token": "local-demo-secret"}).status_code == 200
