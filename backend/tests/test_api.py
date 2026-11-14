import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db


@pytest.fixture
def client():
    app.dependency_overrides.clear()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "CampusRelay",
        "message": "CampusRelay API is running",
    }


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "CampusRelay",
    }


def test_database_health_success(client):
    class FakeDB:
        def execute(self, statement):
            return 1

    app.dependency_overrides[get_db] = lambda: FakeDB()

    response = client.get("/health/database")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "connected",
    }


def test_database_health_failure(client):
    class FakeDB:
        def execute(self, statement):
            raise RuntimeError("Database unavailable")

    app.dependency_overrides[get_db] = lambda: FakeDB()

    response = client.get("/health/database")

    assert response.status_code == 200
    assert response.json() == {
        "status": "error",
        "database": "disconnected",
    }
