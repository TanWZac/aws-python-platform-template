from fastapi.testclient import TestClient

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
