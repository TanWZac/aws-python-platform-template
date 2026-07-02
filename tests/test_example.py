from fastapi.testclient import TestClient

from platform_service.main import app


client = TestClient(app)


def test_example_route() -> None:
    response = client.get("/api/v1/example")

    assert response.status_code == 200
    assert "message" in response.json()
