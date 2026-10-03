from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class EvidenceRef:
    source_type: str
    source_id: str
    label: str
    payload: dict[str, Any] = field(default_factory=dict)

    @property
    def citation(self) -> str:
        return f"[{self.source_type}:{self.source_id}]"

    def to_dict(self):
        data = asdict(self)
        data["citation"] = self.citation
        return data


@dataclass(frozen=True)
class AnalystFinding:
    title: str
    statement: str
    severity: str
    citations: list[str]

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class AnalystReport:
    incident_id: str
    summary: str
    findings: list[AnalystFinding]
    defensive_actions: list[str]
    retrieved_context: list[dict]
    evidence: list[EvidenceRef]
    limitations: list[str]

    def to_dict(self):
        return {
            "incident_id": self.incident_id,
            "summary": self.summary,
            "findings": [finding.to_dict() for finding in self.findings],
            "defensive_actions": list(self.defensive_actions),
            "retrieved_context": list(self.retrieved_context),
            "evidence": [item.to_dict() for item in self.evidence],
            "limitations": list(self.limitations),
        }
