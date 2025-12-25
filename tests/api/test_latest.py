import pytest
from fastapi.testclient import TestClient

from app.api import app


@pytest.fixture
def client():
    return TestClient(app)


def test_latest_not_found_when_empty(client):
    response = client.get("/readings/latest")
    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == "No readings available"
