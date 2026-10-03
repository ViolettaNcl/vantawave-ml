from __future__ import annotations

from pathlib import Path

from vantawave.sensors.base import PassiveSensor, SensorCapability
from vantawave.sensors.events import EventType, WirelessEvent


class ScapyUnavailable(RuntimeError):
    pass


def _require_scapy():
    try:
        from scapy.all import Dot11, Dot11Elt, PcapReader, RadioTap
    except ImportError as exc:
        raise ScapyUnavailable(
            'PCAP replay is optional. Install it with: pip install -e ".[pcap]"'
        ) from exc
    return Dot11, Dot11Elt, PcapReader, RadioTap


def scapy_available() -> bool:
    try:
        import scapy  # noqa: F401
    except ImportError:
        return False
    return True


def _channel_from_frequency(frequency_mhz: int | None) -> int | None:
    if frequency_mhz is None:
        return None
    if frequency_mhz == 2484:
        return 14
    if 2412 <= frequency_mhz <= 2472:
        return (frequency_mhz - 2407) // 5
    if 5000 <= frequency_mhz <= 5900:
        return (frequency_mhz - 5000) // 5
    if 5955 <= frequency_mhz <= 7115:
        return (frequency_mhz - 5950) // 5
    return None


def _event_type(dot11_type: int, subtype: int) -> EventType:
    if dot11_type == 0:
        if subtype == 8:
            return EventType.BEACON
        if subtype == 11:
            return EventType.AUTHENTICATION
        if subtype in {0, 1, 2, 3}:
            return EventType.ASSOCIATION
        if subtype == 12:
            return EventType.DEAUTHENTICATION
        if subtype == 10:
            return EventType.DISASSOCIATION
        return EventType.OTHER_80211
    if dot11_type == 2:
        return EventType.DATA
    return EventType.OTHER_80211


def _derive_bssid(dot11) -> str | None:
    try:
        flags = int(dot11.FCfield)
    except Exception:
        flags = 0

    to_ds = bool(flags & 0x1)
    from_ds = bool(flags & 0x2)

    if not to_ds and not from_ds:
        return getattr(dot11, "addr3", None)
    if to_ds and not from_ds:
        return getattr(dot11, "addr1", None)
    if from_ds and not to_ds:
        return getattr(dot11, "addr2", None)
    return None


def _ssid_from_packet(packet, Dot11Elt) -> str | None:
    layer = packet.getlayer(Dot11Elt)
    while layer is not None:
        if getattr(layer, "ID", None) == 0:
            info = getattr(layer, "info", b"")
            if isinstance(info, bytes):
                return info.decode("utf-8", errors="replace") or None
            return str(info) or None
        layer = getattr(layer, "payload", None)
        if not isinstance(layer, Dot11Elt):
            break
    return None


def packet_to_event(packet) -> WirelessEvent | None:
    Dot11, Dot11Elt, _, RadioTap = _require_scapy()

    if not packet.haslayer(Dot11):
        return None

    dot11 = packet.getlayer(Dot11)
    dot11_type = int(getattr(dot11, "type", -1))
    subtype = int(getattr(dot11, "subtype", -1))

    radiotap = packet.getlayer(RadioTap) if packet.haslayer(RadioTap) else None
    rssi = getattr(radiotap, "dBm_AntSignal", None) if radiotap else None
    frequency = None
    if radiotap is not None:
        for attribute in ("ChannelFrequency", "Channel"):
            value = getattr(radiotap, attribute, None)
            if isinstance(value, int) and value > 1000:
                frequency = value
                break

    try:
        retry = bool(int(dot11.FCfield) & 0x8)
    except Exception:
        retry = None

    timestamp = float(getattr(packet, "time", 0.0))
    from datetime import datetime, timezone
    observed_at = datetime.fromtimestamp(timestamp, timezone.utc).isoformat()

    bssid = _derive_bssid(dot11)
    ssid = _ssid_from_packet(packet, Dot11Elt)

    return WirelessEvent(
        event_type=_event_type(dot11_type, subtype),
        timestamp=observed_at,
        source="pcap-replay",
        ssid=ssid,
        bssid=bssid.lower() if isinstance(bssid, str) else bssid,
        transmitter=getattr(dot11, "addr2", None),
        receiver=getattr(dot11, "addr1", None),
        channel=_channel_from_frequency(frequency),
        frequency_mhz=frequency,
        rssi_dbm=float(rssi) if isinstance(rssi, (int, float)) else None,
        frame_length=int(len(packet)),
        retry=retry,
        metadata={
            "dot11_type": dot11_type,
            "dot11_subtype": subtype,
            "collection_mode": "offline-pcap-replay",
        },
    )


class PcapReplaySensor(PassiveSensor):
    name = "pcap-replay"

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def capability(self) -> SensorCapability:
        if not self.path.exists():
            return SensorCapability(
                name=self.name,
                available=False,
                mode="offline-pcap-replay",
                reason=f"{self.path} does not exist.",
            )
        if not scapy_available():
            return SensorCapability(
                name=self.name,
                available=False,
                mode="offline-pcap-replay",
                reason='Scapy is not installed. Use: pip install -e ".[pcap]"',
            )
        return SensorCapability(
            name=self.name,
            available=True,
            mode="offline-pcap-replay",
            details={
                "path": str(self.path),
                "packet_injection": False,
                "live_capture": False,
            },
        )

    def collect_once(self) -> list[WirelessEvent]:
        capability = self.capability()
        if not capability.available:
            raise RuntimeError(capability.reason or "PCAP replay unavailable.")

        _, _, PcapReader, _ = _require_scapy()
        events = []
        with PcapReader(str(self.path)) as reader:
            for packet in reader:
                event = packet_to_event(packet)
                if event is not None:
                    events.append(event)
        return events
