from __future__ import annotations

from pathlib import Path
import json
import uuid


class CaptureAuditStore:
    def __init__(self, root: str | Path = "artifacts/capture_audit"):
        self.root = Path(root)

    def create_id(self) -> str:
        return uuid.uuid4().hex[:12]

    def audit_dir(self, audit_id: str) -> Path:
        if not audit_id or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789" for ch in audit_id.lower()):
            raise ValueError("Invalid audit ID.")
        return self.root / audit_id

    def capture_path(self, audit_id: str, suffix: str) -> Path:
        suffix = suffix.lower()
        if suffix not in {".pcap", ".pcapng", ".cap"}:
            raise ValueError("Supported capture types: .pcap, .pcapng, .cap")
        path = self.audit_dir(audit_id) / f"capture{suffix}"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def save_report(self, audit_id: str, report: dict) -> Path:
        path = self.audit_dir(audit_id) / "audit.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return path

    def load_report(self, audit_id: str) -> dict:
        path = self.audit_dir(audit_id) / "audit.json"
        if not path.exists():
            raise KeyError(audit_id)
        return json.loads(path.read_text(encoding="utf-8"))

    def delete(self, audit_id: str):
        import shutil
        path = self.audit_dir(audit_id)
        if path.exists():
            shutil.rmtree(path)
