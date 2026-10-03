import pytest
from vantawave.lab.registry import AuthorizedTarget, AuthorizedTargetRegistry

def test_authorized_target_registry_roundtrip(tmp_path):
    registry = AuthorizedTargetRegistry(tmp_path / "targets.json")
    target = AuthorizedTarget(
        name="Lab AP",
        ssid="VantaWave-Lab",
        bssid="00:11:22:33:44:55",
        authorized=True,
        owner_confirmation="I own this laboratory access point.",
    )
    registry.register(target)
    assert registry.get(target.target_id)["ssid"] == "VantaWave-Lab"
    assert registry.require_authorized(target.target_id)["authorized"] is True

def test_unauthorized_target_rejected():
    with pytest.raises(PermissionError):
        AuthorizedTarget(
            name="No",
            ssid="No",
            bssid="00:11:22:33:44:55",
            authorized=False,
            owner_confirmation="not authorized",
        )
