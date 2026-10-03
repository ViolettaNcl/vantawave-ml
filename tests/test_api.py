from fastapi.testclient import TestClient
from vantawave.api.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["version"] == "0.3.0"

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_features():
    response = client.get("/features")
    assert response.status_code == 200
    assert response.json()["count"] == 10

def test_models():
    response = client.get("/models")
    assert "random_forest" in response.json()["classification"]

def test_risk_score():
    response = client.post("/risk/score", json={
        "anomaly_score": 0.9,
        "classifier_confidence": 0.8,
        "repeated_alerts": 4,
        "unknown_device": True,
    })
    assert response.status_code == 200
    assert 0 <= response.json()["score"] <= 100
