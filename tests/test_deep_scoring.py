import numpy as np

from vantawave.ml.deep.scoring import (
    calibrate_reconstruction_threshold,
    evaluate_anomaly_scores,
)


def test_reconstruction_threshold_uses_quantile():
    errors = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    threshold = calibrate_reconstruction_threshold(errors, quantile=0.8)
    assert 0.03 <= threshold <= 0.05


def test_anomaly_metrics_from_scores():
    y = np.array([0, 0, 1, 1])
    scores = np.array([0.1, 0.2, 0.8, 0.9])
    metrics = evaluate_anomaly_scores(y, scores, 0.5)
    assert metrics.f1 == 1.0
    assert metrics.false_positive_rate == 0.0
