from datetime import datetime, timezone

from vantawave.sensors.events import EventType, WirelessEvent
from vantawave.sensors.storage import JsonlEventStore


def test_jsonl_event_roundtrip(tmp_path):
    event = WirelessEvent(
        event_type=EventType.AP_OBSERVATION,
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat(),
        source="test",
        ssid="Lab",
        bssid="00:11:22:33:44:55",
        channel=6,
        signal_percent=70,
    )
    store = JsonlEventStore(tmp_path / "events.jsonl")
    store.append(event)

    loaded = store.read_all()
    assert len(loaded) == 1
    assert loaded[0].event_type == EventType.AP_OBSERVATION
    assert loaded[0].ssid == "Lab"
