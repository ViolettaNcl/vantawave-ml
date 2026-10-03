from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from vantawave.sensors.events import EventType, WirelessEvent
from vantawave.sensors.storage import JsonlEventStore


OUT = Path("data/demo/sensor_events.jsonl")


def main():
    if OUT.exists():
        OUT.unlink()

    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    events = []

    for i in range(20):
        events.append(
            WirelessEvent(
                event_type=EventType.BEACON,
                timestamp=(base + timedelta(seconds=i * 2)).isoformat(),
                source="synthetic-sensor-fixture",
                ssid="VantaWave-Lab",
                bssid="00:11:22:33:44:55",
                transmitter="00:11:22:33:44:55",
                receiver="ff:ff:ff:ff:ff:ff",
                channel=6,
                rssi_dbm=-48.0 - (i % 3),
                frame_length=120,
                retry=False,
                security="WPA2",
            )
        )

    for offset in [5, 15, 25]:
        events.append(
            WirelessEvent(
                event_type=EventType.AUTHENTICATION,
                timestamp=(base + timedelta(seconds=offset)).isoformat(),
                source="synthetic-sensor-fixture",
                bssid="00:11:22:33:44:55",
                transmitter="aa:bb:cc:dd:ee:ff",
                receiver="00:11:22:33:44:55",
                channel=6,
                rssi_dbm=-55.0,
                frame_length=90,
                retry=False,
            )
        )

    events.append(
        WirelessEvent(
            event_type=EventType.DEAUTHENTICATION,
            timestamp=(base + timedelta(seconds=35)).isoformat(),
            source="synthetic-sensor-fixture",
            bssid="00:11:22:33:44:55",
            transmitter="00:11:22:33:44:55",
            receiver="aa:bb:cc:dd:ee:ff",
            channel=6,
            rssi_dbm=-50.0,
            frame_length=80,
            retry=False,
        )
    )

    store = JsonlEventStore(OUT)
    store.write_many(events)

    print(f"Created normalized sensor fixture: {OUT}")
    print(f"Events: {len(events)}")


if __name__ == "__main__":
    main()
