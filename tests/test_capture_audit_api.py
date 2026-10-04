from fastapi.testclient import TestClient

from vantawave.api.main import app
import vantawave.api.capture_audit_routes as routes
from vantawave.capture_audit.aircrack import CandidateVerification


client = TestClient(app)


def test_capture_audit_capabilities():
    response = client.get("/capture-audit/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert body["ssid_only_password_recovery"] is False
    assert body["wordlist_cracking_api"] is False
    assert body["bruteforce_api"] is False


def test_verify_candidate_can_issue_ephemeral_token(monkeypatch):
    monkeypatch.setattr(
        routes.store,
        "load_report",
        lambda audit_id: {
            "audit_id": audit_id,
            "target": {"target_id": "target-1"},
            "capture": {
                "path": "capture.pcap",
                "target_seen": True,
                "candidate_verification_ready": True,
            },
        },
    )
    monkeypatch.setattr(
        routes,
        "_authorized_target",
        lambda target_id: {
            "target_id": target_id,
            "name": "Lab",
            "ssid": "LabWiFi",
            "bssid": "00:11:22:33:44:55",
            "authorized": True,
        },
    )
    monkeypatch.setattr(
        routes,
        "verify_single_candidate",
        lambda **kwargs: CandidateVerification(
            verified=True,
            usable_capture=True,
            tool="aircrack-ng",
            message="verified",
        ),
    )

    response = client.post(
        "/capture-audit/verify-candidate",
        json={
            "audit_id": "abc123",
            "candidate": "CorrectPass123!",
            "security": "WPA2-Personal",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["verified"] is True
    assert body["secret_token"]
    assert "CorrectPass123!" not in str(body)
    assert set(body["masked_secret"]) == {"•"}


def test_verify_candidate_rejects_multiline_wordlist(monkeypatch):
    monkeypatch.setattr(
        routes.store,
        "load_report",
        lambda audit_id: {
            "audit_id": audit_id,
            "target": {"target_id": "target-1"},
            "capture": {
                "path": "capture.pcap",
                "target_seen": True,
                "candidate_verification_ready": True,
            },
        },
    )
    monkeypatch.setattr(
        routes,
        "_authorized_target",
        lambda target_id: {
            "target_id": target_id,
            "name": "Lab",
            "ssid": "LabWiFi",
            "bssid": "00:11:22:33:44:55",
            "authorized": True,
        },
    )

    response = client.post(
        "/capture-audit/verify-candidate",
        json={
            "audit_id": "abc123",
            "candidate": "password1\npassword2",
            "security": "WPA2-Personal",
        },
    )
    assert response.status_code == 400


def test_connect_verified_uses_vault_secret_without_echo(monkeypatch):
    token = routes.vault.put(
        secret="CorrectPass123!",
        ssid="LabWiFi",
        security="WPA2-Personal",
    )

    def fake_connect(ssid, password, *, security):
        assert ssid == "LabWiFi"
        assert password == "CorrectPass123!"
        return {
            "success": True,
            "request_accepted": True,
            "ssid": ssid,
            "security": security,
            "message": "connected",
        }

    monkeypatch.setattr(routes, "connect_with_password", fake_connect)

    response = client.post(
        "/capture-audit/connect-verified",
        json={"token": token},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "CorrectPass123!" not in response.text
