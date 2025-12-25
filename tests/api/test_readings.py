import pytest
from fastapi.testclient import TestClient

from app.api import app


@pytest.fixture
def client():
    return TestClient(app)


def test_readings_empty_list_when_none(client):
    response = client.get("/readings?limit=10")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert data == []
