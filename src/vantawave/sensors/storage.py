from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import uuid

from vantawave.sensors.events import WirelessEvent


@dataclass
class SensorSession:
    source: str
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ended_at: str | None = None
    event_count: int = 0
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


class JsonlEventStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def append(self, event: WirelessEvent):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")

    def write_many(self, events):
        for event in events:
            self.append(event)

    def read_all(self) -> list[WirelessEvent]:
        if not self.path.exists():
            return []
        events = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    events.append(WirelessEvent.from_dict(json.loads(line)))
        return events
