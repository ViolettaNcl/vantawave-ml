from vantawave.sensors.adapters.windows_netsh import (
    parse_netsh_networks,
    signal_percent_to_estimated_dbm,
)
from vantawave.sensors.events import EventType


ENGLISH = r"""
Interface name : Wi-Fi
There are 2 networks currently visible.

SSID 1 : VantaWave-Lab
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP
    BSSID 1                 : 00:11:22:33:44:55
         Signal             : 84%
         Radio type         : 802.11ax
         Channel            : 6
    BSSID 2                 : 00:11:22:33:44:66
         Signal             : 62%
         Radio type         : 802.11ac
         Channel            : 36

SSID 2 : Guest
    Network type            : Infrastructure
    Authentication          : Open
    Encryption              : None
    BSSID 1                 : aa:bb:cc:dd:ee:ff
         Signal             : 40%
         Radio type         : 802.11n
         Channel            : 11
"""


RUSSIAN = r"""
SSID 1 : Lab-RU
    Проверка подлинности    : WPA2-Personal
    Шифрование              : CCMP
    BSSID 1                 : 12:34:56:78:90:ab
         Сигнал             : 76%
         Тип радио          : 802.11ac
         Канал              : 44
"""


def test_parse_english_netsh():
    events = parse_netsh_networks(ENGLISH, observed_at="2026-01-01T00:00:00+00:00")
    assert len(events) == 3

    first = events[0]
    assert first.event_type == EventType.AP_OBSERVATION
    assert first.ssid == "VantaWave-Lab"
    assert first.bssid == "00:11:22:33:44:55"
    assert first.channel == 6
    assert first.signal_percent == 84
    assert first.security == "WPA2-Personal / CCMP"
    assert first.metadata["radio_type"] == "802.11ax"


def test_parse_russian_netsh():
    events = parse_netsh_networks(RUSSIAN, observed_at="2026-01-01T00:00:00+00:00")
    assert len(events) == 1
    assert events[0].ssid == "Lab-RU"
    assert events[0].channel == 44
    assert events[0].signal_percent == 76


def test_signal_percent_estimate_is_bounded():
    assert signal_percent_to_estimated_dbm(100) == -50
    assert signal_percent_to_estimated_dbm(0) == -100
    assert signal_percent_to_estimated_dbm(200) == -50
