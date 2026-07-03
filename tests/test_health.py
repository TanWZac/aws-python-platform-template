from fastapi.testclient import TestClient

from platform_service.core.config import settings
from platform_service.main import app


client = TestClient(app)


def test_live_health_check() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "live"


def test_ready_health_check() -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert "app" in body
    assert "dependencies" in body


def test_live_health_includes_security_headers_and_request_id() -> None:
    response = client.get("/health/live", headers={"X-Request-ID": "req-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-123"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_ready_health_reports_not_ready_when_dependency_fails(monkeypatch) -> None:
    monkeypatch.setattr(settings, "readiness_check_urls", "http://127.0.0.1:9/unreachable")
    monkeypatch.setattr(settings, "readiness_timeout_seconds", 0.05)

    response = client.get("/health/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["dependencies"][0]["status"] == "not_ready"


def test_ready_health_reports_not_ready_while_shutting_down() -> None:
    app.state.is_shutting_down = True
    try:
        response = client.get("/health/ready")
    finally:
        app.state.is_shutting_down = False

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
