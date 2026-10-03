from __future__ import annotations

from dataclasses import asdict, dataclass
import pandas as pd


@dataclass(frozen=True)
class NumericBaseline:
    mean: float
    std: float

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class DriftFinding:
    feature: str
    kind: str
    score: float
    severity: str

    def to_dict(self):
        return asdict(self)


def build_drift_baseline(frame: pd.DataFrame) -> dict:
    numeric = {}
    categorical = {}

    for column in frame.columns:
        series = frame[column]
        if pd.api.types.is_numeric_dtype(series):
            mean = float(series.mean())
            std = float(series.std(ddof=0))
            numeric[str(column)] = NumericBaseline(mean, std).to_dict()
        else:
            frequencies = series.astype("string").value_counts(normalize=True, dropna=False)
            categorical[str(column)] = {
                str(key): float(value)
                for key, value in frequencies.to_dict().items()
            }

    return {
        "rows": int(len(frame)),
        "numeric": numeric,
        "categorical": categorical,
    }


def compare_to_baseline(
    baseline: dict,
    current: pd.DataFrame,
    *,
    numeric_warning_z: float = 1.0,
    numeric_high_z: float = 2.0,
    categorical_warning_tv: float = 0.15,
    categorical_high_tv: float = 0.30,
) -> list[DriftFinding]:
    findings = []

    for feature, stats in baseline.get("numeric", {}).items():
        if feature not in current.columns:
            continue
        current_mean = float(pd.to_numeric(current[feature], errors="coerce").mean())
        std = float(stats["std"])
        reference_mean = float(stats["mean"])
        scale = std if std > 1e-12 else max(abs(reference_mean), 1.0)
        score = abs(current_mean - reference_mean) / scale

        severity = "ok"
        if score >= numeric_high_z:
            severity = "high"
        elif score >= numeric_warning_z:
            severity = "warning"

        findings.append(
            DriftFinding(feature, "numeric_mean_shift_z", float(score), severity)
        )

    for feature, reference in baseline.get("categorical", {}).items():
        if feature not in current.columns:
            continue
        current_freq = (
            current[feature]
            .astype("string")
            .value_counts(normalize=True, dropna=False)
            .to_dict()
        )
        keys = set(reference) | {str(k) for k in current_freq}
        tv = 0.0
        for key in keys:
            tv += abs(
                float(reference.get(key, 0.0))
                - float(current_freq.get(key, current_freq.get(str(key), 0.0)))
            )
        tv *= 0.5

        severity = "ok"
        if tv >= categorical_high_tv:
            severity = "high"
        elif tv >= categorical_warning_tv:
            severity = "warning"

        findings.append(
            DriftFinding(feature, "categorical_total_variation", float(tv), severity)
        )

    return findings
