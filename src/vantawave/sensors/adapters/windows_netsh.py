from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import platform
import re
import shutil
import subprocess

from vantawave.sensors.base import PassiveSensor, SensorCapability
from vantawave.sensors.events import EventType, WirelessEvent


SSID_RE = re.compile(r"^\s*SSID\s+\d+\s*:\s*(.*)$", re.IGNORECASE)
BSSID_RE = re.compile(r"^\s*BSSID\s+\d+\s*:\s*([0-9A-Fa-f:.-]+)\s*$", re.IGNORECASE)
SIGNAL_RE = re.compile(r"^\s*(Signal|Сигнал)\s*:\s*(\d+)%", re.IGNORECASE)
CHANNEL_RE = re.compile(r"^\s*(Channel|Канал)\s*:\s*(\d+)", re.IGNORECASE)
AUTH_RE = re.compile(
    r"^\s*(Authentication|Проверка подлинности|Аутентификация)\s*:\s*(.*)$",
    re.IGNORECASE,
)
ENCRYPTION_RE = re.compile(
    r"^\s*(Encryption|Шифрование)\s*:\s*(.*)$",
    re.IGNORECASE,
)
RADIO_RE = re.compile(
    r"^\s*(Radio type|Тип радио|Тип радиосвязи)\s*:\s*(.*)$",
    re.IGNORECASE,
)


def signal_percent_to_estimated_dbm(percent: float) -> float:
    percent = max(0.0, min(100.0, float(percent)))
    # Approximation only. Windows exposes signal quality, not calibrated RSSI here.
    return percent / 2.0 - 100.0


@dataclass
class _Network:
    ssid: str = ""
    authentication: str | None = None
    encryption: str | None = None


@dataclass
class _Bssid:
    bssid: str
    signal_percent: float | None = None
    channel: int | None = None
    radio_type: str | None = None


def parse_netsh_networks(output: str, *, observed_at: str | None = None) -> list[WirelessEvent]:
    observed_at = observed_at or datetime.now(timezone.utc).isoformat()

    current_network = _Network()
    current_bssid: _Bssid | None = None
    events: list[WirelessEvent] = []

    def flush_bssid():
        nonlocal current_bssid
        if current_bssid is None:
            return

        signal = current_bssid.signal_percent
        security_parts = [
            value
            for value in [current_network.authentication, current_network.encryption]
            if value
        ]
        security = " / ".join(security_parts) if security_parts else None

        events.append(
            WirelessEvent(
                event_type=EventType.AP_OBSERVATION,
                timestamp=observed_at,
                source="windows-netsh",
                ssid=current_network.ssid or None,
                bssid=current_bssid.bssid.lower(),
                channel=current_bssid.channel,
                signal_percent=signal,
                rssi_dbm=(
                    signal_percent_to_estimated_dbm(signal)
                    if signal is not None
                    else None
                ),
                security=security,
                metadata={
                    "radio_type": current_bssid.radio_type,
                    "rssi_estimated": signal is not None,
                    "collection_mode": "os-wlan-discovery",
                },
            )
        )
        current_bssid = None

    for raw_line in output.splitlines():
        line = raw_line.rstrip()

        ssid_match = SSID_RE.match(line)
        if ssid_match:
            flush_bssid()
            current_network = _Network(ssid=ssid_match.group(1).strip())
            continue

        auth_match = AUTH_RE.match(line)
        if auth_match and current_bssid is None:
            current_network.authentication = auth_match.group(2).strip()
            continue

        encryption_match = ENCRYPTION_RE.match(line)
        if encryption_match and current_bssid is None:
            current_network.encryption = encryption_match.group(2).strip()
            continue

        bssid_match = BSSID_RE.match(line)
        if bssid_match:
            flush_bssid()
            current_bssid = _Bssid(bssid=bssid_match.group(1).strip())
            continue

        if current_bssid is None:
            continue

        signal_match = SIGNAL_RE.match(line)
        if signal_match:
            current_bssid.signal_percent = float(signal_match.group(2))
            continue

        channel_match = CHANNEL_RE.match(line)
        if channel_match:
            current_bssid.channel = int(channel_match.group(2))
            continue

        radio_match = RADIO_RE.match(line)
        if radio_match:
            current_bssid.radio_type = radio_match.group(2).strip()
            continue

    flush_bssid()
    return events


class WindowsNetshSensor(PassiveSensor):
    name = "windows-netsh"

    def capability(self) -> SensorCapability:
        windows = platform.system().lower() == "windows"
        netsh = shutil.which("netsh") is not None
        available = windows and netsh

        reason = None
        if not windows:
            reason = "WindowsNetshSensor only runs on Windows."
        elif not netsh:
            reason = "netsh was not found in PATH."

        return SensorCapability(
            name=self.name,
            available=available,
            mode="os-wlan-discovery",
            reason=reason,
            details={
                "command": "netsh wlan show networks mode=bssid",
                "packet_injection": False,
                "monitor_mode_required": False,
            },
        )

    def collect_once(self) -> list[WirelessEvent]:
        capability = self.capability()
        if not capability.available:
            raise RuntimeError(capability.reason or "Windows netsh sensor unavailable.")

        process = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True,
            check=False,
        )

        # netsh output encoding follows the Windows console code page.
        candidates = ["utf-8", "cp866", "cp1251", "mbcs"]
        output = None
        for encoding in candidates:
            try:
                output = process.stdout.decode(encoding)
                break
            except (UnicodeDecodeError, LookupError):
                continue
        if output is None:
            output = process.stdout.decode(errors="replace")

        if process.returncode != 0:
            stderr = process.stderr.decode(errors="replace")
            raise RuntimeError(
                f"netsh WLAN scan failed with exit code {process.returncode}: {stderr}"
            )

        return parse_netsh_networks(output)
