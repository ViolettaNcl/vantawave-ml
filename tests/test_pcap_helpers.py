from vantawave.sensors.events import EventType
from vantawave.sensors.pcap.replay import (
    _channel_from_frequency,
    _event_type,
    scapy_available,
)


def test_channel_conversion():
    assert _channel_from_frequency(2412) == 1
    assert _channel_from_frequency(2437) == 6
    assert _channel_from_frequency(5180) == 36


def test_dot11_event_mapping():
    assert _event_type(0, 8) == EventType.BEACON
    assert _event_type(0, 11) == EventType.AUTHENTICATION
    assert _event_type(0, 12) == EventType.DEAUTHENTICATION
    assert _event_type(2, 0) == EventType.DATA


def test_scapy_capability_returns_boolean():
    assert isinstance(scapy_available(), bool)
