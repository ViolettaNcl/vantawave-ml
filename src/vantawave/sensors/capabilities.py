from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib.util import find_spec
import ctypes
import platform
import shutil


@dataclass(frozen=True)
class HostCapabilities:
    operating_system: str
    release: str
    python_version: str
    netsh_available: bool
    scapy_available: bool
    windows_admin: bool | None
    passive_windows_scan: bool
    pcap_replay: bool
    raw_80211_live_capture: str

    def to_dict(self):
        return asdict(self)


def _windows_admin() -> bool | None:
    if platform.system().lower() != "windows":
        return None
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return None


def detect_host_capabilities() -> HostCapabilities:
    system = platform.system()
    netsh = shutil.which("netsh") is not None
    scapy = find_spec("scapy") is not None

    return HostCapabilities(
        operating_system=system,
        release=platform.release(),
        python_version=platform.python_version(),
        netsh_available=netsh,
        scapy_available=scapy,
        windows_admin=_windows_admin(),
        passive_windows_scan=(system.lower() == "windows" and netsh),
        pcap_replay=scapy,
        raw_80211_live_capture=(
            "not implemented in v0.7; hardware/driver-specific monitor mode belongs to authorized lab work"
        ),
    )
