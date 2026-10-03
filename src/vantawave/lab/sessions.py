from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
import json
import uuid

from vantawave.lab.registry import AuthorizedTargetRegistry


class LabSessionStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class LabSession:
    target_id: str
    mode: str
    sensor_source: str
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    status: LabSessionStatus = LabSessionStatus.CREATED
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: str | None = None
    ended_at: str | None = None
    before_features: dict | None = None
    after_features: dict | None = None
    sensor_session_path: str | None = None
    notes: str | None = None
    error: str | None = None

    def to_dict(self):
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, payload: dict):
        return cls(
            target_id=payload["target_id"],
            mode=payload["mode"],
            sensor_source=payload["sensor_source"],
            session_id=payload["session_id"],
            status=LabSessionStatus(payload["status"]),
            created_at=payload["created_at"],
            started_at=payload.get("started_at"),
            ended_at=payload.get("ended_at"),
            before_features=payload.get("before_features"),
            after_features=payload.get("after_features"),
            sensor_session_path=payload.get("sensor_session_path"),
            notes=payload.get("notes"),
            error=payload.get("error"),
        )


class LabSessionStore:
    def __init__(
        self,
        path: str | Path = "artifacts/lab/sessions.json",
        target_registry: AuthorizedTargetRegistry | None = None,
    ):
        self.path = Path(path)
        self.target_registry = target_registry or AuthorizedTargetRegistry()

    def _load(self) -> dict:
        if not self.path.exists():
            return {"sessions": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, payload: dict):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def create(self, *, target_id: str, mode: str, sensor_source: str, notes: str | None = None):
        self.target_registry.require_authorized(target_id)
        session = LabSession(
            target_id=target_id,
            mode=mode,
            sensor_source=sensor_source,
            notes=notes,
        )
        payload = self._load()
        payload["sessions"].append(session.to_dict())
        self._save(payload)
        return session

    def list_sessions(self) -> list[dict]:
        return self._load()["sessions"]

    def get(self, session_id: str) -> LabSession:
        for payload in self._load()["sessions"]:
            if payload["session_id"] == session_id:
                return LabSession.from_dict(payload)
        raise KeyError(session_id)

    def save(self, session: LabSession):
        payload = self._load()
        replaced = False
        for index, item in enumerate(payload["sessions"]):
            if item["session_id"] == session.session_id:
                payload["sessions"][index] = session.to_dict()
                replaced = True
                break
        if not replaced:
            payload["sessions"].append(session.to_dict())
        self._save(payload)
        return session

    def start(self, session_id: str):
        session = self.get(session_id)
        if session.status not in {LabSessionStatus.CREATED, LabSessionStatus.FAILED}:
            raise ValueError(f"Cannot start session in status {session.status.value}.")
        session.status = LabSessionStatus.RUNNING
        session.started_at = datetime.now(timezone.utc).isoformat()
        session.error = None
        return self.save(session)

    def complete(
        self,
        session_id: str,
        *,
        before_features: dict | None,
        after_features: dict | None,
        sensor_session_path: str | None = None,
    ):
        session = self.get(session_id)
        if session.status != LabSessionStatus.RUNNING:
            raise ValueError("Only running sessions can be completed.")
        session.status = LabSessionStatus.COMPLETED
        session.ended_at = datetime.now(timezone.utc).isoformat()
        session.before_features = before_features
        session.after_features = after_features
        session.sensor_session_path = sensor_session_path
        return self.save(session)

    def fail(self, session_id: str, error: str):
        session = self.get(session_id)
        session.status = LabSessionStatus.FAILED
        session.ended_at = datetime.now(timezone.utc).isoformat()
        session.error = error
        return self.save(session)
