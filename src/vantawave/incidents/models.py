from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import uuid

@dataclass
class Incident:
    network: str
    anomaly_score: float
    predicted_class: str
    confidence: float
    severity: str
    model_name: str
    model_version: str
    evidence: dict
    incident_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self):
        return asdict(self)
