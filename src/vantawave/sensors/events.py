from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import uuid


class EventType(str, Enum):
    AP_OBSERVATION = "ap_observation"
    BEACON = "beacon"
    AUTHENTICATION = "authentication"
    ASSOCIATION = "association"
    DEAUTHENTICATION = "deauthentication"
    DISASSOCIATION = "disassociation"
    DATA = "data"
    OTHER_80211 = "other_80211"


@dataclass(frozen=True)
class WirelessEvent:
    event_type: EventType
    timestamp: str
    source: str
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    ssid: str | None = None
    bssid: str | None = None
    transmitter: str | None = None
    receiver: str | None = None
    channel: int | None = None
    frequency_mhz: int | None = None
    signal_percent: float | None = None
    rssi_dbm: float | None = None
    frame_length: int | None = None
    retry: bool | None = None
    security: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["event_type"] = self.event_type.value
        return data

    @classmethod
    def now(cls, *, event_type: EventType, source: str, **kwargs):
        return cls(
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            source=source,
            **kwargs,
        )

    @classmethod
    def from_dict(cls, payload: dict):
        return cls(
            event_type=EventType(payload["event_type"]),
            timestamp=str(payload["timestamp"]),
            source=str(payload["source"]),
            event_id=str(payload.get("event_id") or uuid.uuid4().hex[:12]),
            ssid=payload.get("ssid"),
            bssid=payload.get("bssid"),
            transmitter=payload.get("transmitter"),
            receiver=payload.get("receiver"),
            channel=payload.get("channel"),
            frequency_mhz=payload.get("frequency_mhz"),
            signal_percent=payload.get("signal_percent"),
            rssi_dbm=payload.get("rssi_dbm"),
            frame_length=payload.get("frame_length"),
            retry=payload.get("retry"),
            security=payload.get("security"),
            metadata=dict(payload.get("metadata") or {}),
        )
