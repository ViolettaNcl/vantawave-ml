from fastapi.testclient import TestClient

from vantawave.api.main import app
import vantawave.api.wifi_recovery_routes as routes


client = TestClient(app)


def test_wifi_recovery_capabilities():
    response = client.get("/wifi-recovery/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert body["unknown_wpa2_wpa3_password_recovery"] is False
    assert body["connect_with_supplied_password"] is True


def test_password_strength_endpoint_is_local_and_does_not_return_password():
    response = client.post(
        "/wifi-recovery/password-strength",
        json={"password": "StrongPass123!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "score" in body
    assert "password" not in body


def test_saved_key_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("VANTAWAVE_ALLOW_LOCAL_CREDENTIAL_VIEW", raising=False)
    response = client.post(
        "/wifi-recovery/saved-key",
        json={"ssid": "Lab", "explicit_confirmation": True},
    )
    assert response.status_code == 403


def test_connect_endpoint_uses_supplied_password_without_echo(monkeypatch):
    def fake_connect(ssid, password, *, security):
        assert ssid == "Lab"
        assert password == "StrongPass123!"
        return {
            "success": True,
            "ssid": ssid,
            "security": security,
            "message": "ok",
        }

    monkeypatch.setattr(routes, "connect_with_password", fake_connect)

    response = client.post(
        "/wifi-recovery/connect",
        json={
            "ssid": "Lab",
            "password": "StrongPass123!",
            "security": "WPA2-Personal",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "password" not in body
