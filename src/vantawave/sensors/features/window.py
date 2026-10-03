from __future__ import annotations

from collections import Counter, deque
from dataclasses import asdict, dataclass
from datetime import datetime
import statistics

from vantawave.sensors.events import EventType, WirelessEvent


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@dataclass(frozen=True)
class WindowFeatures:
    window_start: str
    window_end: str
    duration_seconds: float
    total_events: int
    event_rate: float
    auth_rate: float
    assoc_rate: float
    deauth_rate: float
    disassoc_rate: float
    beacon_rate: float
    data_rate: float
    ap_observation_rate: float
    unique_bssids: int
    unique_transmitters: int
    unique_ssids: int
    rssi_mean: float
    rssi_std: float
    signal_percent_mean: float
    retry_ratio: float
    channel_count: int
    event_type_counts: dict[str, int]

    def to_dict(self):
        return asdict(self)

    def to_legacy_feature_row(self) -> dict[str, float]:
        return {
            "auth_rate": self.auth_rate,
            "assoc_rate": self.assoc_rate,
            "deauth_rate": self.deauth_rate,
            "beacon_rate": self.beacon_rate,
            "unique_clients": float(self.unique_transmitters),
            "unique_bssids": float(self.unique_bssids),
            "rssi_mean": self.rssi_mean,
            "rssi_std": self.rssi_std,
            "retry_ratio": self.retry_ratio,
            "event_rate": self.event_rate,
        }


def aggregate_events(
    events: list[WirelessEvent],
    *,
    duration_seconds: float | None = None,
) -> WindowFeatures:
    if not events:
        raise ValueError("At least one event is required.")

    ordered = sorted(events, key=lambda event: _parse_timestamp(event.timestamp))
    start = _parse_timestamp(ordered[0].timestamp)
    end = _parse_timestamp(ordered[-1].timestamp)

    if duration_seconds is None:
        duration_seconds = max((end - start).total_seconds(), 1.0)
    duration_seconds = max(float(duration_seconds), 1e-9)

    counts = Counter(event.event_type.value for event in ordered)
    rate = lambda event_type: counts[event_type.value] / duration_seconds

    bssids = {e.bssid for e in ordered if e.bssid}
    transmitters = {e.transmitter for e in ordered if e.transmitter}
    ssids = {e.ssid for e in ordered if e.ssid}
    channels = {e.channel for e in ordered if e.channel is not None}

    rssi = [float(e.rssi_dbm) for e in ordered if e.rssi_dbm is not None]
    signal = [
        float(e.signal_percent)
        for e in ordered
        if e.signal_percent is not None
    ]
    retries = [e.retry for e in ordered if e.retry is not None]

    return WindowFeatures(
        window_start=start.isoformat(),
        window_end=end.isoformat(),
        duration_seconds=duration_seconds,
        total_events=len(ordered),
        event_rate=len(ordered) / duration_seconds,
        auth_rate=rate(EventType.AUTHENTICATION),
        assoc_rate=rate(EventType.ASSOCIATION),
        deauth_rate=rate(EventType.DEAUTHENTICATION),
        disassoc_rate=rate(EventType.DISASSOCIATION),
        beacon_rate=rate(EventType.BEACON),
        data_rate=rate(EventType.DATA),
        ap_observation_rate=rate(EventType.AP_OBSERVATION),
        unique_bssids=len(bssids),
        unique_transmitters=len(transmitters),
        unique_ssids=len(ssids),
        rssi_mean=float(statistics.mean(rssi)) if rssi else 0.0,
        rssi_std=float(statistics.pstdev(rssi)) if len(rssi) > 1 else 0.0,
        signal_percent_mean=float(statistics.mean(signal)) if signal else 0.0,
        retry_ratio=(
            float(sum(bool(value) for value in retries) / len(retries))
            if retries
            else 0.0
        ),
        channel_count=len(channels),
        event_type_counts=dict(counts),
    )


class RollingWindowAggregator:
    def __init__(self, window_seconds: float = 60.0):
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive.")
        self.window_seconds = float(window_seconds)
        self._events = deque()

    def add(self, event: WirelessEvent):
        self._events.append(event)
        self._expire(_parse_timestamp(event.timestamp))

    def extend(self, events):
        for event in events:
            self.add(event)

    def _expire(self, current: datetime):
        while self._events:
            first = _parse_timestamp(self._events[0].timestamp)
            if (current - first).total_seconds() <= self.window_seconds:
                break
            self._events.popleft()

    def snapshot(self) -> WindowFeatures | None:
        if not self._events:
            return None
        return aggregate_events(
            list(self._events),
            duration_seconds=self.window_seconds,
        )

    @property
    def event_count(self) -> int:
        return len(self._events)
