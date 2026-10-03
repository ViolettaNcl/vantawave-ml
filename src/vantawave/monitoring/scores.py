from __future__ import annotations

from dataclasses import asdict, dataclass
import numpy as np


@dataclass(frozen=True)
class ScoreBaseline:
    mean: float
    std: float
    p50: float
    p90: float
    p95: float
    p99: float

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class ScoreDriftResult:
    mean_shift_z: float
    reference_mean: float
    current_mean: float
    reference_p95: float
    current_p95: float
    exceedance_rate_reference_p95: float
    severity: str

    def to_dict(self):
        return asdict(self)


def build_score_baseline(scores) -> ScoreBaseline:
    values = np.asarray(scores, dtype=float)
    if values.size == 0:
        raise ValueError("At least one score is required.")
    return ScoreBaseline(
        mean=float(values.mean()),
        std=float(values.std()),
        p50=float(np.quantile(values, 0.50)),
        p90=float(np.quantile(values, 0.90)),
        p95=float(np.quantile(values, 0.95)),
        p99=float(np.quantile(values, 0.99)),
    )


def compare_score_drift(
    baseline: ScoreBaseline | dict,
    current_scores,
    *,
    warning_z: float = 1.0,
    high_z: float = 2.0,
) -> ScoreDriftResult:
    if isinstance(baseline, dict):
        baseline = ScoreBaseline(**baseline)

    current = np.asarray(current_scores, dtype=float)
    if current.size == 0:
        raise ValueError("At least one current score is required.")

    scale = baseline.std if baseline.std > 1e-12 else max(abs(baseline.mean), 1.0)
    shift = abs(float(current.mean()) - baseline.mean) / scale

    severity = "ok"
    if shift >= high_z:
        severity = "high"
    elif shift >= warning_z:
        severity = "warning"

    return ScoreDriftResult(
        mean_shift_z=float(shift),
        reference_mean=baseline.mean,
        current_mean=float(current.mean()),
        reference_p95=baseline.p95,
        current_p95=float(np.quantile(current, 0.95)),
        exceedance_rate_reference_p95=float((current > baseline.p95).mean()),
        severity=severity,
    )
