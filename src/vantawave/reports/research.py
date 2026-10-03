from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

@dataclass(frozen=True)
class ModelEvaluation:
    model: str
    validation: dict
    test: dict
    training_seconds: float
    artifact_path: str | None = None

    def to_dict(self):
        return asdict(self)

def save_research_report(
    *,
    dataset_profile: dict,
    leakage_findings: list[dict],
    evaluations: list[ModelEvaluation],
    feature_importance: list[dict],
    output: str | Path,
):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "dataset_profile": dataset_profile,
        "leakage_findings": leakage_findings,
        "models": [item.to_dict() for item in evaluations],
        "feature_importance": feature_importance,
    }
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output
