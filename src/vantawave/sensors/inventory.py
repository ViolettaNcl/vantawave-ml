from __future__ import annotations

from dataclasses import asdict, dataclass

from vantawave.sensors.events import EventType, WirelessEvent


@dataclass
class AccessPointRecord:
    bssid: str
    ssid: str | None
    security: str | None
    channel: int | None
    signal_percent: float | None
    rssi_dbm: float | None
    first_seen: str
    last_seen: str
    observations: int = 1

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class InventoryChange:
    change_type: str
    bssid: str
    timestamp: str
    before: dict | None
    after: dict

    def to_dict(self):
        return asdict(self)


class NetworkInventory:
    def __init__(self):
        self._aps: dict[str, AccessPointRecord] = {}

    def update(self, events: list[WirelessEvent]) -> list[InventoryChange]:
        changes: list[InventoryChange] = []

        for event in events:
            if event.event_type not in {EventType.AP_OBSERVATION, EventType.BEACON}:
                continue
            if not event.bssid:
                continue

            key = event.bssid.lower()
            existing = self._aps.get(key)

            if existing is None:
                record = AccessPointRecord(
                    bssid=key,
                    ssid=event.ssid,
                    security=event.security,
                    channel=event.channel,
                    signal_percent=event.signal_percent,
                    rssi_dbm=event.rssi_dbm,
                    first_seen=event.timestamp,
                    last_seen=event.timestamp,
                )
                self._aps[key] = record
                changes.append(
                    InventoryChange(
                        change_type="new_bssid",
                        bssid=key,
                        timestamp=event.timestamp,
                        before=None,
                        after=record.to_dict(),
                    )
                )
                continue

            before = existing.to_dict()
            changed_fields = []

            for field_name in ("ssid", "security", "channel"):
                incoming = getattr(event, field_name)
                current = getattr(existing, field_name)
                if incoming is not None and current is not None and incoming != current:
                    changed_fields.append(field_name)
                if incoming is not None:
                    setattr(existing, field_name, incoming)

            if event.signal_percent is not None:
                existing.signal_percent = event.signal_percent
            if event.rssi_dbm is not None:
                existing.rssi_dbm = event.rssi_dbm

            existing.last_seen = event.timestamp
            existing.observations += 1

            for field_name in changed_fields:
                changes.append(
                    InventoryChange(
                        change_type=f"{field_name}_changed",
                        bssid=key,
                        timestamp=event.timestamp,
                        before=before,
                        after=existing.to_dict(),
                    )
                )

        return changes

    def snapshot(self) -> list[dict]:
        return [
            record.to_dict()
            for record in sorted(self._aps.values(), key=lambda item: item.bssid)
        ]

    def get(self, bssid: str) -> dict | None:
        record = self._aps.get(bssid.lower())
        return record.to_dict() if record else None

    def __len__(self):
        return len(self._aps)
