from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class EvaluationPolicy:
    interval_hours: int = 24
    high_drift_limit: int = 1
    warning_drift_limit: int = 3
    min_f1: float = 0.80
    max_fpr: float = 0.10

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class RetrainingRecommendation:
    recommended: bool
    priority: str
    reasons: list[str]
    next_evaluation_at: str

    def to_dict(self):
        return asdict(self)


def evaluation_due(last_evaluated_at: str | None, policy: EvaluationPolicy | None = None) -> bool:
    policy = policy or EvaluationPolicy()
    if not last_evaluated_at:
        return True
    last = datetime.fromisoformat(last_evaluated_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    return now >= last + timedelta(hours=policy.interval_hours)


def recommend_retraining(
    *,
    drift_findings: list[dict],
    performance_metrics: dict | None = None,
    policy: EvaluationPolicy | None = None,
) -> RetrainingRecommendation:
    policy = policy or EvaluationPolicy()
    reasons = []

    high = sum(item.get("severity") == "high" for item in drift_findings)
    warning = sum(item.get("severity") == "warning" for item in drift_findings)

    if high >= policy.high_drift_limit:
        reasons.append(f"{high} high-severity drift finding(s)")
    if warning >= policy.warning_drift_limit:
        reasons.append(f"{warning} warning-level drift finding(s)")

    metrics = performance_metrics or {}
    if "f1" in metrics and float(metrics["f1"]) < policy.min_f1:
        reasons.append(f"F1 {float(metrics['f1']):.4f} below {policy.min_f1:.4f}")
    if (
        "false_positive_rate" in metrics
        and float(metrics["false_positive_rate"]) > policy.max_fpr
    ):
        reasons.append(
            f"FPR {float(metrics['false_positive_rate']):.4f} above "
            f"{policy.max_fpr:.4f}"
        )

    recommended = bool(reasons)
    priority = "none"
    if recommended:
        priority = "high" if high or any("F1" in reason for reason in reasons) else "medium"

    next_at = datetime.now(timezone.utc) + timedelta(hours=policy.interval_hours)
    return RetrainingRecommendation(
        recommended=recommended,
        priority=priority,
        reasons=reasons or ["No retraining trigger reached."],
        next_evaluation_at=next_at.isoformat(),
    )
