import numpy as np

from vantawave.ml.calibration.thresholds import (
    calibrate_threshold,
    score_threshold,
)


def test_threshold_calibration_selects_feasible_threshold():
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    scores = np.array([0.05, 0.10, 0.20, 0.45, 0.55, 0.70, 0.85, 0.95])
    result = calibrate_threshold(
        y,
        scores,
        min_precision=0.75,
        max_false_positive_rate=0.30,
    )
    assert 0.05 <= result.threshold <= 0.95
    assert result.validation.f1 > 0.0


def test_score_threshold_reports_fpr():
    y = np.array([0, 0, 1, 1])
    scores = np.array([0.1, 0.9, 0.8, 0.7])
    result = score_threshold(y, scores, 0.5)
    assert result.false_positive_rate == 0.5
    assert result.recall == 1.0
