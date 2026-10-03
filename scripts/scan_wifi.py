from __future__ import annotations

import argparse
import json
from pathlib import Path

from vantawave.sensors.adapters.windows_netsh import WindowsNetshSensor
from vantawave.sensors.collector import collect_sensor_session


def main():
    parser = argparse.ArgumentParser(
        description="Passive Windows Wi-Fi scan using the OS WLAN interface."
    )
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--window", type=float, default=60.0)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/sensors/live"),
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run exactly one passive scan.",
    )
    args = parser.parse_args()

    sensor = WindowsNetshSensor()

    if args.once:
        events = sensor.collect_once()
        print(json.dumps([event.to_dict() for event in events], indent=2, ensure_ascii=False))
        print(f"\nObserved BSSIDs: {len(events)}")
        return

    payload = collect_sensor_session(
        sensor,
        duration_seconds=args.duration,
        interval_seconds=args.interval,
        window_seconds=args.window,
        event_path=args.out / "events.jsonl",
        feature_path=args.out / "features.jsonl",
        session_path=args.out / "session.json",
        inventory_path=args.out / "inventory.json",
        changes_path=args.out / "inventory_changes.jsonl",
    )

    print("VantaWave passive sensor session complete")
    print(f"session_id: {payload['session_id']}")
    print(f"events: {payload['event_count']}")
    print(f"iterations: {payload['iterations']}")
    print(f"feature snapshots: {payload['feature_snapshots']}")
    print(f"events file: {payload['event_path']}")
    print(f"features file: {payload['feature_path']}")
    print(f"inventory: {payload['inventory_path']}")
    print(f"inventory size: {payload['inventory_size']}")
    print(f"inventory changes: {payload['changes_path']}")


if __name__ == "__main__":
    main()
