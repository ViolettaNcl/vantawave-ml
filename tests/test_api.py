from fastapi.testclient import TestClient
from vantawave.api.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["project"] == "VantaWave ML"
    assert body["version"] == "0.5.0"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_features():
    response = client.get("/features")
    assert response.status_code == 200
    assert response.json()["count"] == 10


def test_models():
    response = client.get("/models")
    assert response.status_code == 200
    assert "random_forest" in response.json()["classification"]


def test_risk_score():
    response = client.post(
        "/risk/score",
        json={
            "anomaly_score": 0.9,
            "classifier_confidence": 0.8,
            "repeated_alerts": 4,
            "unknown_device": True,
        },
    )
    assert response.status_code == 200
    assert 0 <= response.json()["score"] <= 100


def test_awid3_schema():
    response = client.get("/research/awid3/schema")
    assert response.status_code == 200
    body = response.json()
    assert body["feature_count"] == 16
    assert "frame.len" in body["numeric"]


def test_mlops_capabilities():
    response = client.get("/mlops/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert body["local_registry"] is True
    assert body["threshold_calibration"] is True


def test_registry_models_empty_without_artifacts(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    response = client.get("/registry/models")
    assert response.status_code == 200
    assert response.json() == {"models": []}


def test_promotion_policy_endpoint():
    response = client.get("/promotion/policy")
    assert response.status_code == 200
    assert "min_test_f1" in response.json()


def test_experiments_empty_without_artifacts(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    response = client.get("/experiments")
    assert response.status_code == 200
    assert response.json() == {"runs": []}
