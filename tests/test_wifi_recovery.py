from types import SimpleNamespace

import pytest

from vantawave.wifi_recovery.recovery import recovery_options
from vantawave.wifi_recovery.strength import audit_password_strength
from vantawave.wifi_recovery.windows import (
    _profile_xml,
    parse_saved_profiles_output,
)


def test_parse_saved_profiles_english_and_russian():
    output = """
    All User Profile     : Home WiFi
    Current User Profile : Test Lab
    Профиль всех пользователей : Домашняя сеть
    """
    names = [item.name for item in parse_saved_profiles_output(output)]
    assert "Home WiFi" in names
    assert "Test Lab" in names
    assert "Домашняя сеть" in names


def test_profile_xml_escapes_user_values_and_supports_wpa2():
    xml = _profile_xml(
        'Lab & Home',
        'Safe<Pass>123!',
        security="WPA2-Personal",
    )
    assert "<authentication>WPA2PSK</authentication>" in xml
    assert "Lab &amp; Home" in xml
    assert "Safe&lt;Pass&gt;123!" in xml


def test_profile_xml_supports_wpa3():
    xml = _profile_xml(
        "Lab",
        "StrongPass123!",
        security="WPA3-Personal",
    )
    assert "<authentication>WPA3SAE</authentication>" in xml


def test_profile_xml_rejects_short_passphrase():
    with pytest.raises(ValueError):
        _profile_xml("Lab", "short", security="WPA2-Personal")


def test_password_strength_distinguishes_weak_and_strong():
    weak = audit_password_strength("password123")
    strong = audit_password_strength("J9!mQ2#rT7$wP4@x")
    assert strong.score > weak.score
    assert weak.rating in {"very_weak", "weak"}


def test_recovery_options_explain_unsaved_network():
    options = recovery_options(
        saved_profile_exists=False,
        gateway_available=False,
    )
    saved = next(item for item in options if item["id"] == "saved_profile")
    assert saved["available"] is False
    assert "no saved" in saved["description"].lower()
