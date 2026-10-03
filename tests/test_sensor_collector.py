from datetime import datetime, timezone

from vantawave.sensors.base import PassiveSensor, SensorCapability
from vantawave.sensors.collector import collect_sensor_session
from vantawave.sensors.events import EventType, WirelessEvent


class FakeSensor(PassiveSensor):
    name = "fake"

    def capability(self):
        return SensorCapability(
            name=self.name,
            available=True,
            mode="test",
        )

    def collect_once(self):
        return [
            WirelessEvent(
                event_type=EventType.AP_OBSERVATION,
                timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat(),
                source=self.name,
                ssid="Lab",
                bssid="00:11:22:33:44:55",
                channel=6,
                signal_percent=80,
            )
        ]


def test_collect_sensor_session_writes_files(tmp_path):
    payload = collect_sensor_session(
        FakeSensor(),
        duration_seconds=0,
        interval_seconds=1,
        event_path=tmp_path / "events.jsonl",
        feature_path=tmp_path / "features.jsonl",
        session_path=tmp_path / "session.json",
        inventory_path=tmp_path / "inventory.json",
        changes_path=tmp_path / "changes.jsonl",
        max_iterations=1,
    )

    assert payload["event_count"] == 1
    assert payload["iterations"] == 1
    assert (tmp_path / "events.jsonl").exists()
    assert (tmp_path / "features.jsonl").exists()
    assert (tmp_path / "session.json").exists()
    assert (tmp_path / "inventory.json").exists()
    assert (tmp_path / "changes.jsonl").exists()
    assert payload["inventory_size"] == 1
