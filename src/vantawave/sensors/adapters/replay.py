from __future__ import annotations

from pathlib import Path

from vantawave.sensors.base import PassiveSensor, SensorCapability
from vantawave.sensors.events import WirelessEvent
from vantawave.sensors.storage import JsonlEventStore


class JsonlReplaySensor(PassiveSensor):
    name = "jsonl-replay"

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def capability(self) -> SensorCapability:
        return SensorCapability(
            name=self.name,
            available=self.path.exists(),
            mode="offline-replay",
            reason=None if self.path.exists() else f"{self.path} does not exist.",
            details={"path": str(self.path), "packet_injection": False},
        )

    def collect_once(self) -> list[WirelessEvent]:
        capability = self.capability()
        if not capability.available:
            raise FileNotFoundError(self.path)
        return JsonlEventStore(self.path).read_all()
