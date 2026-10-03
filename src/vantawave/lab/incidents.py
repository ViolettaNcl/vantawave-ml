from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import uuid

from vantawave.risk.engine import RiskInput, calculate_risk


@dataclass
class LabIncident:
    session_id: str
    target_id: str
    title: str
    severity: str
    risk_score: int
    evidence: dict
    incident_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self):
        return asdict(self)


def generate_lab_incident(
    *,
    session_id: str,
    target_id: str,
    anomaly_score: float,
    classifier_confidence: float,
    repeated_alerts: int,
    unknown_device: bool,
    evidence: dict,
) -> LabIncident:
    risk = calculate_risk(
        RiskInput(
            anomaly_score=anomaly_score,
            classifier_confidence=classifier_confidence,
            repeated_alerts=repeated_alerts,
            unknown_device=unknown_device,
        )
    )
    return LabIncident(
        session_id=session_id,
        target_id=target_id,
        title="Authorized lab telemetry anomaly",
        severity=risk.severity,
        risk_score=risk.score,
        evidence=evidence,
    )
