from fastapi.testclient import TestClient

from platform_service.core.config import settings
from platform_service.main import app


client = TestClient(app)


def test_example_route() -> None:
    response = client.get("/api/v1/example")

    assert response.status_code == 200
    assert "message" in response.json()


def test_example_route_requires_api_key_when_auth_enabled(monkeypatch) -> None:
    monkeypatch.setattr(settings, "auth_enabled", True)
    monkeypatch.setattr(settings, "api_keys", "expected-key")

    response = client.get("/api/v1/example")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_example_route_accepts_valid_api_key_when_auth_enabled(monkeypatch) -> None:
    monkeypatch.setattr(settings, "auth_enabled", True)
    monkeypatch.setattr(settings, "api_keys", "expected-key")

    response = client.get("/api/v1/example", headers={"X-API-Key": "expected-key"})

    assert response.status_code == 200
    assert "message" in response.json()
