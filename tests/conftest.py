import pytest
from fastapi.testclient import TestClient

from platform_service.main import app


@pytest.fixture
def client() -> TestClient:
    """Shared FastAPI test client. Each test gets a fresh request context."""
    with TestClient(app) as c:
        yield c
