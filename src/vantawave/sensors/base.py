from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Iterable

from vantawave.sensors.events import WirelessEvent


@dataclass(frozen=True)
class SensorCapability:
    name: str
    available: bool
    mode: str
    reason: str | None = None
    details: dict | None = None

    def to_dict(self):
        return asdict(self)


class PassiveSensor(ABC):
    name: str

    @abstractmethod
    def capability(self) -> SensorCapability:
        raise NotImplementedError

    @abstractmethod
    def collect_once(self) -> list[WirelessEvent]:
        raise NotImplementedError

    def collect(self, *, iterations: int = 1) -> Iterable[WirelessEvent]:
        for _ in range(iterations):
            yield from self.collect_once()
