from datetime import datetime, timedelta, timezone

from vantawave.sensors.events import EventType, WirelessEvent
from vantawave.sensors.features.window import (
    RollingWindowAggregator,
    aggregate_events,
)


def event(kind, seconds, *, retry=False, bssid="00:11:22:33:44:55"):
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return WirelessEvent(
        event_type=kind,
        timestamp=(base + timedelta(seconds=seconds)).isoformat(),
        source="test",
        bssid=bssid,
        transmitter="aa:bb:cc:dd:ee:ff",
        channel=6,
        rssi_dbm=-50 + seconds * 0.01,
        retry=retry,
    )


def test_aggregate_sensor_events():
    events = [
        event(EventType.BEACON, 0),
        event(EventType.BEACON, 10),
        event(EventType.AUTHENTICATION, 20),
        event(EventType.DEAUTHENTICATION, 30, retry=True),
    ]
    features = aggregate_events(events, duration_seconds=60)
    assert features.total_events == 4
    assert features.beacon_rate == 2 / 60
    assert features.auth_rate == 1 / 60
    assert features.deauth_rate == 1 / 60
    assert features.retry_ratio == 0.25
    assert features.unique_bssids == 1

    legacy = features.to_legacy_feature_row()
    assert set(legacy) == {
        "auth_rate",
        "assoc_rate",
        "deauth_rate",
        "beacon_rate",
        "unique_clients",
        "unique_bssids",
        "rssi_mean",
        "rssi_std",
        "retry_ratio",
        "event_rate",
    }


def test_rolling_window_expires_old_events():
    window = RollingWindowAggregator(window_seconds=60)
    window.add(event(EventType.BEACON, 0))
    window.add(event(EventType.BEACON, 61))
    assert window.event_count == 1
