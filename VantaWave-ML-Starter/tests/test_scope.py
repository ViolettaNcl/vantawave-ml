import pytest
from vantawave.lab.scope import LabTarget, require_authorized_target

def test_rejects_unapproved_target():
    target = LabTarget(
        name="unknown",
        ssid="Nearby-WiFi",
        bssid="AA:BB:CC:DD:EE:FF",
        authorized=False,
    )
    with pytest.raises(PermissionError):
        require_authorized_target(target)

def test_accepts_registered_lab_target():
    target = LabTarget(
        name="lab",
        ssid="VantaWave-Lab-WiFi",
        bssid="00:11:22:33:44:55",
        authorized=True,
    )
    require_authorized_target(target)
