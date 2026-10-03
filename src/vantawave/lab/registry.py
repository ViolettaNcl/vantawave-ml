from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import uuid


BSSID_RE = re.compile(r"^(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$")


@dataclass
class AuthorizedTarget:
    name: str
    ssid: str
    bssid: str
    authorized: bool
    owner_confirmation: str
    notes: str | None = None
    target_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        self.bssid = self.bssid.lower()
        if not self.name.strip():
            raise ValueError("Target name cannot be empty.")
        if not self.ssid.strip():
            raise ValueError("SSID cannot be empty.")
        if not BSSID_RE.match(self.bssid):
            raise ValueError("BSSID must use colon-separated hexadecimal bytes.")
        if not self.authorized:
            raise PermissionError("Only explicitly authorized targets may be registered.")
        if len(self.owner_confirmation.strip()) < 8:
            raise ValueError("owner_confirmation must explicitly document authorization.")

    def to_dict(self):
        return asdict(self)


class AuthorizedTargetRegistry:
    def __init__(self, path: str | Path = "artifacts/lab/targets.json"):
        self.path = Path(path)

    def _load(self) -> dict:
        if not self.path.exists():
            return {"targets": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, payload: dict):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def register(self, target: AuthorizedTarget) -> AuthorizedTarget:
        payload = self._load()
        for existing in payload["targets"]:
            if existing["bssid"].lower() == target.bssid.lower():
                raise ValueError(f"BSSID {target.bssid} is already registered.")
        payload["targets"].append(target.to_dict())
        self._save(payload)
        return target

    def list_targets(self) -> list[dict]:
        return self._load()["targets"]

    def get(self, target_id: str) -> dict:
        for target in self._load()["targets"]:
            if target["target_id"] == target_id:
                return target
        raise KeyError(target_id)

    def require_authorized(self, target_id: str) -> dict:
        target = self.get(target_id)
        if not target.get("authorized"):
            raise PermissionError("Target is not authorized.")
        return target
