from datetime import datetime, timedelta, timezone

from vantawave.sensors.events import EventType, WirelessEvent
from vantawave.sensors.replay import replay_jsonl
from vantawave.sensors.storage import JsonlEventStore


def test_replay_jsonl_returns_features(tmp_path):
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    events = [
        WirelessEvent(
            event_type=EventType.BEACON,
            timestamp=base.isoformat(),
            source="fixture",
            bssid="00:11:22:33:44:55",
            transmitter="00:11:22:33:44:55",
            channel=6,
            rssi_dbm=-50,
            retry=False,
        ),
        WirelessEvent(
            event_type=EventType.AUTHENTICATION,
            timestamp=(base + timedelta(seconds=5)).isoformat(),
            source="fixture",
            bssid="00:11:22:33:44:55",
            transmitter="aa:bb:cc:dd:ee:ff",
            channel=6,
            rssi_dbm=-55,
            retry=False,
        ),
    ]
    path = tmp_path / "events.jsonl"
    JsonlEventStore(path).write_many(events)

    payload = replay_jsonl(path, window_seconds=60)
    assert payload["events"] == 2
    assert payload["features"]["total_events"] == 2
    assert payload["legacy_features"]["auth_rate"] > 0
