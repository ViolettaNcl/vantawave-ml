from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib


class CaptureAuditUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class CaptureAuditResult:
    path: str
    sha256: str
    target_id: str
    target_ssid: str
    target_bssid: str
    total_packets: int
    dot11_packets: int
    target_packets: int
    eapol_packets: int
    target_eapol_packets: int
    observed_ssids: list[str]
    observed_bssids: list[str]
    observed_clients: list[str]
    target_seen: bool
    likely_handshake_evidence: bool
    candidate_verification_ready: bool
    notes: list[str]

    def to_dict(self):
        return asdict(self)


def sha256_file(path: str | Path) -> str:
    path = Path(path)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_scapy():
    try:
        from scapy.all import Dot11, Dot11Elt, PcapReader
        from scapy.layers.eap import EAPOL
    except ImportError as exc:
        raise CaptureAuditUnavailable(
            'Capture audit requires Scapy. Install: pip install -e ".[pcap]"'
        ) from exc
    return Dot11, Dot11Elt, PcapReader, EAPOL



def _derive_bssid(dot11) -> str | None:
    try:
        flags = int(dot11.FCfield)
    except Exception:
        flags = 0

    to_ds = bool(flags & 0x1)
    from_ds = bool(flags & 0x2)

    if not to_ds and not from_ds:
        value = getattr(dot11, "addr3", None)
    elif to_ds and not from_ds:
        value = getattr(dot11, "addr1", None)
    elif from_ds and not to_ds:
        value = getattr(dot11, "addr2", None)
    else:
        value = None

    return str(value).lower() if value else None


def _ssid(packet, Dot11Elt) -> str | None:
    layer = packet.getlayer(Dot11Elt)
    while layer is not None:
        if getattr(layer, "ID", None) == 0:
            info = getattr(layer, "info", b"")
            if isinstance(info, bytes):
                value = info.decode("utf-8", errors="replace")
            else:
                value = str(info)
            return value or None
        layer = getattr(layer, "payload", None)
        if not isinstance(layer, Dot11Elt):
            break
    return None


def analyze_capture(
    path: str | Path,
    *,
    target: dict,
) -> CaptureAuditResult:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    Dot11, Dot11Elt, PcapReader, EAPOL = _require_scapy()

    target_bssid = str(target["bssid"]).lower()
    target_ssid = str(target["ssid"])

    total = 0
    dot11_count = 0
    target_packets = 0
    eapol_count = 0
    target_eapol = 0
    ssids: set[str] = set()
    bssids: set[str] = set()
    clients: set[str] = set()

    with PcapReader(str(path)) as reader:
        for packet in reader:
            total += 1
            if not packet.haslayer(Dot11):
                continue

            dot11_count += 1
            dot11 = packet.getlayer(Dot11)
            addresses = {
                str(value).lower()
                for value in (
                    getattr(dot11, "addr1", None),
                    getattr(dot11, "addr2", None),
                    getattr(dot11, "addr3", None),
                )
                if value
            }

            derived_bssid = _derive_bssid(dot11)
            if derived_bssid:
                bssids.add(derived_bssid)

            observed_ssid = _ssid(packet, Dot11Elt)
            if observed_ssid:
                ssids.add(observed_ssid)

            packet_targets_lab = (
                derived_bssid == target_bssid or observed_ssid == target_ssid
            )
            if packet_targets_lab:
                target_packets += 1
                for address in addresses:
                    if address != target_bssid and address != "ff:ff:ff:ff:ff:ff":
                        clients.add(address)

            if packet.haslayer(EAPOL):
                eapol_count += 1
                if packet_targets_lab:
                    target_eapol += 1

    target_seen = target_packets > 0
    likely_handshake = target_eapol >= 2
    ready = target_seen and target_eapol > 0

    notes = []
    if not target_seen:
        notes.append(
            "The authorized target SSID/BSSID was not observed in this capture."
        )
    if target_seen and target_eapol == 0:
        notes.append(
            "Target traffic is present, but no EAPOL authentication frames were found."
        )
    if target_eapol == 1:
        notes.append(
            "One target EAPOL frame was found; this is usually insufficient for candidate verification."
        )
    if likely_handshake:
        notes.append(
            "Multiple target EAPOL frames were found. Aircrack-ng can determine whether the capture is usable for WPA/WPA2 candidate verification."
        )
    notes.append(
        "This audit does not derive a password. It only reports authentication evidence for an explicitly authorized target."
    )

    return CaptureAuditResult(
        path=str(path),
        sha256=sha256_file(path),
        target_id=str(target["target_id"]),
        target_ssid=target_ssid,
        target_bssid=target_bssid,
        total_packets=total,
        dot11_packets=dot11_count,
        target_packets=target_packets,
        eapol_packets=eapol_count,
        target_eapol_packets=target_eapol,
        observed_ssids=sorted(ssids),
        observed_bssids=sorted(bssids),
        observed_clients=sorted(clients),
        target_seen=target_seen,
        likely_handshake_evidence=likely_handshake,
        candidate_verification_ready=ready,
        notes=notes,
    )
