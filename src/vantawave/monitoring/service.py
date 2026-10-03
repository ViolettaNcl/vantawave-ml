from __future__ import annotations

from dataclasses import dataclass
import uuid

import pandas as pd

from vantawave.db.repositories import DriftRepository, EvaluationRepository
from vantawave.ml.drift.baseline import build_drift_baseline, compare_to_baseline
from vantawave.monitoring.policy import EvaluationPolicy, recommend_retraining
from vantawave.monitoring.scores import build_score_baseline, compare_score_drift


@dataclass
class MonitoringResult:
    feature_baseline: dict
    drift_findings: list[dict]
    score_baseline: dict | None
    score_drift: dict | None
    retraining: dict

    def to_dict(self):
        return {
            "feature_baseline": self.feature_baseline,
            "drift_findings": self.drift_findings,
            "score_baseline": self.score_baseline,
            "score_drift": self.score_drift,
            "retraining": self.retraining,
        }


def evaluate_monitoring_window(
    *,
    reference_features: pd.DataFrame,
    current_features: pd.DataFrame,
    reference_scores=None,
    current_scores=None,
    performance_metrics: dict | None = None,
    policy: EvaluationPolicy | None = None,
) -> MonitoringResult:
    feature_baseline = build_drift_baseline(reference_features)
    drift = compare_to_baseline(feature_baseline, current_features)
    drift_payload = [item.to_dict() for item in drift]

    score_baseline = None
    score_drift = None
    if reference_scores is not None and current_scores is not None:
        score_baseline_obj = build_score_baseline(reference_scores)
        score_baseline = score_baseline_obj.to_dict()
        score_drift_obj = compare_score_drift(score_baseline_obj, current_scores)
        score_drift = score_drift_obj.to_dict()
        drift_payload.append(
            {
                "feature": "anomaly_score",
                "kind": "anomaly_score_mean_shift",
                "score": score_drift_obj.mean_shift_z,
                "severity": score_drift_obj.severity,
            }
        )

    recommendation = recommend_retraining(
        drift_findings=drift_payload,
        performance_metrics=performance_metrics,
        policy=policy,
    )

    return MonitoringResult(
        feature_baseline=feature_baseline,
        drift_findings=drift_payload,
        score_baseline=score_baseline,
        score_drift=score_drift,
        retraining=recommendation.to_dict(),
    )


def persist_monitoring_result(
    *,
    db_session,
    result: MonitoringResult,
    model_name: str,
    dataset_name: str,
    performance_metrics: dict | None = None,
    baseline_version: str = "v1",
):
    drift_repo = DriftRepository(db_session)
    for item in result.drift_findings:
        drift_repo.add(
            drift_id=uuid.uuid4().hex[:12],
            feature=item["feature"],
            kind=item["kind"],
            score=float(item["score"]),
            severity=item["severity"],
            baseline_version=baseline_version,
            metadata={"model_name": model_name},
        )

    evaluation = EvaluationRepository(db_session).add(
        model_name=model_name,
        dataset_name=dataset_name,
        metrics=performance_metrics or {},
        recommendation=(
            "retrain" if result.retraining["recommended"] else "keep_current_model"
        ),
        reasons=list(result.retraining["reasons"]),
    )
    return evaluation
