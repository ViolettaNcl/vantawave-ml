from __future__ import annotations

from pathlib import Path

from vantawave.sensors.features.window import RollingWindowAggregator
from vantawave.sensors.storage import JsonlEventStore


def replay_jsonl(
    path: str | Path,
    *,
    window_seconds: float = 60.0,
) -> dict:
    events = JsonlEventStore(path).read_all()
    if not events:
        return {
            "events": 0,
            "window_seconds": window_seconds,
            "features": None,
        }

    window = RollingWindowAggregator(window_seconds=window_seconds)
    window.extend(events)
    snapshot = window.snapshot()

    return {
        "events": len(events),
        "window_seconds": window_seconds,
        "features": snapshot.to_dict() if snapshot else None,
        "legacy_features": snapshot.to_legacy_feature_row() if snapshot else None,
    }
