from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class LabTarget:
    name: str
    ssid: str
    bssid: str
    authorized: bool

def require_authorized_target(target: LabTarget) -> None:
    if not target.authorized:
        raise PermissionError(
            "Active lab actions are disabled for targets that are not explicitly authorized."
        )
    if not target.bssid.strip():
        raise ValueError("An authorized lab target must have an explicit BSSID.")
