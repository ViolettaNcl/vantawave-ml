from __future__ import annotations
from dataclasses import asdict, dataclass
import re
import pandas as pd

LEAKAGE_NAME_PATTERNS = [
    r"(^|[._-])(label|target|attack[_ -]?map|ground[_ -]?truth)([._-]|$)",
    r"(^|[._-])(prediction|predicted[_ -]?class)([._-]|$)",
]

@dataclass(frozen=True)
class LeakageFinding:
    column: str
    reason: str
    severity: str = "error"

    def to_dict(self):
        return asdict(self)

def audit_feature_names(columns) -> list[LeakageFinding]:
    findings = []
    for column in map(str, columns):
        lowered = column.lower()
        if any(re.search(pattern, lowered) for pattern in LEAKAGE_NAME_PATTERNS):
            findings.append(
                LeakageFinding(
                    column=column,
                    reason="Column name suggests direct target/ground-truth information.",
                )
            )
    return findings

def audit_exact_target_copies(frame: pd.DataFrame, target: str) -> list[LeakageFinding]:
    if target not in frame.columns:
        return []

    findings = []
    y = frame[target]
    for column in frame.columns:
        if column == target:
            continue
        candidate = frame[column]
        if candidate.equals(y):
            findings.append(
                LeakageFinding(
                    column=str(column),
                    reason=f"Feature is an exact copy of target '{target}'.",
                )
            )
    return findings
