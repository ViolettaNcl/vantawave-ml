from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import platform
import shutil
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

from vantawave.sensors.adapters.windows_netsh import WindowsNetshSensor


class WiFiRecoveryUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class SavedProfile:
    name: str

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class CurrentWiFi:
    state: str | None
    ssid: str | None
    bssid: str | None
    signal_percent: float | None
    channel: int | None
    interface_name: str | None

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class GatewayInfo:
    interface_alias: str | None
    interface_index: int | None
    gateway: str | None

    def to_dict(self):
        return asdict(self)


def _require_windows():
    if platform.system().lower() != "windows":
        raise WiFiRecoveryUnavailable("Wi-Fi Recovery is currently implemented for Windows.")
    if shutil.which("netsh") is None:
        raise WiFiRecoveryUnavailable("netsh was not found in PATH.")


def _run_netsh(*args: str) -> subprocess.CompletedProcess:
    _require_windows()
    return subprocess.run(
        ["netsh", "wlan", *args],
        capture_output=True,
        check=False,
    )


def _decode_windows(data: bytes) -> str:
    for encoding in ("utf-8", "cp866", "cp1251", "mbcs"):
        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            pass
    return data.decode(errors="replace")


def parse_saved_profiles_output(output: str) -> list[SavedProfile]:
    profiles = []
    seen = set()

    for line in output.splitlines():
        if ":" not in line:
            continue
        left, right = line.split(":", 1)
        left_lower = left.lower()
        if (
            "all user profile" in left_lower
            or "current user profile" in left_lower
            or "профиль всех пользователей" in left_lower
            or "профиль текущего пользователя" in left_lower
        ):
            name = right.strip()
            if name and name not in seen:
                seen.add(name)
                profiles.append(SavedProfile(name=name))

    return profiles


def list_saved_profiles() -> list[SavedProfile]:
    result = _run_netsh("show", "profiles")
    if result.returncode != 0:
        raise RuntimeError(_decode_windows(result.stderr) or "Could not list Wi-Fi profiles.")

    return parse_saved_profiles_output(_decode_windows(result.stdout))


def profile_exists(name: str) -> bool:
    return any(profile.name == name for profile in list_saved_profiles())


def export_saved_key(profile_name: str, *, allow_secret: bool = False) -> str | None:
    if not allow_secret:
        raise PermissionError("Saved-key export requires explicit local confirmation.")

    if not profile_exists(profile_name):
        return None

    with tempfile.TemporaryDirectory(prefix="vantawave-wifi-") as tmp:
        result = _run_netsh(
            "export",
            "profile",
            f"name={profile_name}",
            f"folder={tmp}",
            "key=clear",
        )
        if result.returncode != 0:
            raise RuntimeError(
                _decode_windows(result.stderr)
                or "Windows could not export the saved Wi-Fi profile."
            )

        for xml_path in Path(tmp).glob("*.xml"):
            try:
                root = ET.parse(xml_path).getroot()
            except ET.ParseError:
                continue
            for element in root.iter():
                if element.tag.endswith("keyMaterial") and element.text:
                    return element.text.strip()

    return None


def nearby_networks() -> list[dict]:
    sensor = WindowsNetshSensor()
    return [event.to_dict() for event in sensor.collect_once()]


def current_wifi() -> CurrentWiFi:
    result = _run_netsh("show", "interfaces")
    if result.returncode != 0:
        raise RuntimeError(_decode_windows(result.stderr) or "Could not inspect Wi-Fi interface.")

    values = {}
    for line in _decode_windows(result.stdout).splitlines():
        if ":" not in line:
            continue
        key, value = [part.strip() for part in line.split(":", 1)]
        values[key.lower()] = value

    def first(*names):
        for name in names:
            if name.lower() in values:
                return values[name.lower()]
        return None

    signal_raw = first("Signal", "Сигнал")
    signal = None
    if signal_raw and signal_raw.endswith("%"):
        try:
            signal = float(signal_raw[:-1].strip())
        except ValueError:
            pass

    channel_raw = first("Channel", "Канал")
    channel = None
    try:
        if channel_raw:
            channel = int(channel_raw)
    except ValueError:
        pass

    return CurrentWiFi(
        state=first("State", "Состояние"),
        ssid=first("SSID"),
        bssid=first("BSSID"),
        signal_percent=signal,
        channel=channel,
        interface_name=first("Name", "Имя"),
    )


def gateway_info() -> list[GatewayInfo]:
    _require_windows()
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        return []

    command = (
        "Get-NetIPConfiguration | "
        "Where-Object {$_.IPv4DefaultGateway -ne $null} | "
        "Select-Object InterfaceAlias,InterfaceIndex,"
        "@{Name='Gateway';Expression={$_.IPv4DefaultGateway.NextHop}} | "
        "ConvertTo-Json -Compress"
    )
    result = subprocess.run(
        [powershell, "-NoProfile", "-Command", command],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    if isinstance(payload, dict):
        payload = [payload]

    return [
        GatewayInfo(
            interface_alias=item.get("InterfaceAlias"),
            interface_index=item.get("InterfaceIndex"),
            gateway=item.get("Gateway"),
        )
        for item in payload
    ]


def _profile_xml(ssid: str, password: str, *, security: str) -> str:
    if len(password) < 8 or len(password) > 63:
        raise ValueError("WPA2/WPA3 passphrase must contain 8–63 characters.")

    security_map = {
        "WPA2-Personal": "WPA2PSK",
        "WPA3-Personal": "WPA3SAE",
    }
    authentication = security_map.get(security)
    if authentication is None:
        raise ValueError("Supported security modes: WPA2-Personal, WPA3-Personal.")

    safe_ssid = escape(ssid)
    safe_password = escape(password)

    return f'''<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
  <name>{safe_ssid}</name>
  <SSIDConfig>
    <SSID><name>{safe_ssid}</name></SSID>
  </SSIDConfig>
  <connectionType>ESS</connectionType>
  <connectionMode>auto</connectionMode>
  <autoSwitch>false</autoSwitch>
  <MSM>
    <security>
      <authEncryption>
        <authentication>{authentication}</authentication>
        <encryption>AES</encryption>
        <useOneX>false</useOneX>
      </authEncryption>
      <sharedKey>
        <keyType>passPhrase</keyType>
        <protected>false</protected>
        <keyMaterial>{safe_password}</keyMaterial>
      </sharedKey>
    </security>
  </MSM>
</WLANProfile>'''


def connect_with_password(
    ssid: str,
    password: str,
    *,
    security: str = "WPA2-Personal",
) -> dict:
    _require_windows()
    if not ssid.strip():
        raise ValueError("SSID is required.")

    profile_xml = _profile_xml(ssid.strip(), password, security=security)

    with tempfile.TemporaryDirectory(prefix="vantawave-connect-") as tmp:
        profile_path = Path(tmp) / "profile.xml"
        profile_path.write_text(profile_xml, encoding="utf-8")

        add = _run_netsh(
            "add",
            "profile",
            f"filename={profile_path}",
            "user=current",
        )
        if add.returncode != 0:
            raise RuntimeError(
                _decode_windows(add.stderr)
                or _decode_windows(add.stdout)
                or "Windows rejected the Wi-Fi profile."
            )

    connect = _run_netsh(
        "connect",
        f"name={ssid}",
        f"ssid={ssid}",
    )

    request_accepted = connect.returncode == 0
    connected = False

    if request_accepted:
        for _ in range(8):
            try:
                status = current_wifi()
                if status.ssid == ssid:
                    connected = True
                    break
            except Exception:
                pass
            time.sleep(1)

    return {
        "success": connected,
        "request_accepted": request_accepted,
        "ssid": ssid,
        "security": security,
        "message": (
            "Windows connected to the requested SSID."
            if connected
            else (
                "Windows accepted the connection request, but VantaWave could not "
                "confirm the SSID connection."
                if request_accepted
                else
                "Windows could not connect with the supplied credentials/profile."
            )
        ),
    }


def delete_saved_profile(ssid: str) -> dict:
    result = _run_netsh("delete", "profile", f"name={ssid}")
    return {
        "success": result.returncode == 0,
        "ssid": ssid,
        "message": (
            "Saved Wi-Fi profile removed."
            if result.returncode == 0
            else (_decode_windows(result.stderr) or _decode_windows(result.stdout)).strip()
        ),
    }
