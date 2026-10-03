from fastapi.testclient import TestClient
from vantawave.api.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["project"] == "VantaWave ML"
    assert body["status"] == "running"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
