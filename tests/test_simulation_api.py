from fastapi.testclient import TestClient

from vantawave.api.main import app


client = TestClient(app)


def test_simulation_capabilities():
    response = client.get("/simulation/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert body["synthetic_only"] is True
    assert body["transmits_packets"] is False
    assert body["active_attack_execution"] is False


def test_simulation_scenarios():
    response = client.get("/simulation/scenarios")
    assert response.status_code == 200
    scenarios = response.json()["scenarios"]
    assert any(item["scenario_id"] == "deauth_burst" for item in scenarios)


def test_run_simulation_endpoint(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    response = client.post(
        "/simulation/run",
        json={
            "scenario_id": "auth_storm",
            "intensity": 3,
            "duration_seconds": 60,
            "seed": 42,
            "persist_report": True,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["simulated_only"] is True
    assert body["transmits_packets"] is False
    assert body["risk"]["score"] >= 0
    assert "report_paths" in body
