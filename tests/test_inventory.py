from vantawave.sensors.events import EventType, WirelessEvent
from vantawave.sensors.inventory import NetworkInventory


def obs(*, channel=6, security="WPA2", timestamp="2026-01-01T00:00:00+00:00"):
    return WirelessEvent(
        event_type=EventType.AP_OBSERVATION,
        timestamp=timestamp,
        source="test",
        ssid="Lab",
        bssid="00:11:22:33:44:55",
        channel=channel,
        signal_percent=80,
        security=security,
    )


def test_inventory_detects_new_ap_and_channel_change():
    inventory = NetworkInventory()

    first = inventory.update([obs()])
    assert len(first) == 1
    assert first[0].change_type == "new_bssid"
    assert len(inventory) == 1

    second = inventory.update(
        [obs(channel=11, timestamp="2026-01-01T00:01:00+00:00")]
    )
    assert any(change.change_type == "channel_changed" for change in second)
    assert inventory.get("00:11:22:33:44:55")["channel"] == 11
