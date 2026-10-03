import numpy as np

from vantawave.monitoring.scores import build_score_baseline, compare_score_drift


def test_anomaly_score_drift_detects_shift():
    reference = np.array([0.10, 0.11, 0.09, 0.12, 0.10])
    current = np.array([0.30, 0.31, 0.28, 0.35])
    baseline = build_score_baseline(reference)
    drift = compare_score_drift(baseline, current)
    assert drift.mean_shift_z > 1
    assert drift.severity in {"warning", "high"}
