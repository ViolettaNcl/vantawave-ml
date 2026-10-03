from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import time

from vantawave.sensors.base import PassiveSensor
from vantawave.sensors.features.window import RollingWindowAggregator
from vantawave.sensors.inventory import NetworkInventory
from vantawave.sensors.storage import JsonlEventStore, SensorSession


def collect_sensor_session(
    sensor: PassiveSensor,
    *,
    duration_seconds: float = 30.0,
    interval_seconds: float = 5.0,
    event_path: str | Path = "artifacts/sensors/events.jsonl",
    feature_path: str | Path = "artifacts/sensors/features.jsonl",
    session_path: str | Path = "artifacts/sensors/session.json",
    inventory_path: str | Path = "artifacts/sensors/inventory.json",
    changes_path: str | Path = "artifacts/sensors/inventory_changes.jsonl",
    window_seconds: float = 60.0,
    max_iterations: int | None = None,
) -> dict:
    if duration_seconds < 0:
        raise ValueError("duration_seconds cannot be negative.")
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive.")

    capability = sensor.capability()
    if not capability.available:
        raise RuntimeError(capability.reason or f"{sensor.name} is unavailable.")

    event_store = JsonlEventStore(event_path)
    feature_path = Path(feature_path)
    session_path = Path(session_path)
    inventory_path = Path(inventory_path)
    changes_path = Path(changes_path)
    window = RollingWindowAggregator(window_seconds=window_seconds)
    inventory = NetworkInventory()

    session = SensorSession(
        source=sensor.name,
        metadata={
            "mode": capability.mode,
            "window_seconds": window_seconds,
            "interval_seconds": interval_seconds,
            "passive": True,
        },
    )

    started = time.monotonic()
    iterations = 0
    feature_snapshots = 0

    while True:
        events = sensor.collect_once()
        event_store.write_many(events)
        window.extend(events)
        changes = inventory.update(events)
        session.event_count += len(events)
        iterations += 1

        if changes:
            changes_path.parent.mkdir(parents=True, exist_ok=True)
            with changes_path.open("a", encoding="utf-8") as handle:
                for change in changes:
                    handle.write(
                        json.dumps(change.to_dict(), ensure_ascii=False) + "\n"
                    )

        snapshot = window.snapshot()
        if snapshot is not None:
            feature_path.parent.mkdir(parents=True, exist_ok=True)
            with feature_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(snapshot.to_dict(), ensure_ascii=False) + "\n")
            feature_snapshots += 1

        if max_iterations is not None and iterations >= max_iterations:
            break

        elapsed = time.monotonic() - started
        if elapsed >= duration_seconds:
            break

        remaining = duration_seconds - elapsed
        if remaining <= 0:
            break
        time.sleep(min(interval_seconds, remaining))

    session.ended_at = datetime.now(timezone.utc).isoformat()

    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text(
        json.dumps(inventory.snapshot(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    payload = {
        **session.to_dict(),
        "iterations": iterations,
        "feature_snapshots": feature_snapshots,
        "event_path": str(Path(event_path)),
        "feature_path": str(feature_path),
        "inventory_path": str(inventory_path),
        "changes_path": str(changes_path),
        "inventory_size": len(inventory),
    }

    session_path.parent.mkdir(parents=True, exist_ok=True)
    session_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload
