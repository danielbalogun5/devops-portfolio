import json
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Spin the Wheel" in response.data


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"


def test_spin_returns_winner(client):
    payload = {"items": ["Alice", "Bob", "Charlie"]}
    response = client.post("/spin", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "winner" in data
    assert data["winner"] in payload["items"]
    assert "winner_index" in data
    assert 0 <= data["winner_index"] < len(payload["items"])


def test_spin_with_single_item(client):
    payload = {"items": ["Only One"]}
    response = client.post("/spin", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["winner"] == "Only One"
    assert data["winner_index"] == 0


def test_spin_with_empty_items(client):
    payload = {"items": []}
    response = client.post("/spin", json=payload)
    assert response.status_code == 400


def test_spin_uses_default_when_no_items_key(client):
    response = client.post("/spin", json={})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "winner" in data
