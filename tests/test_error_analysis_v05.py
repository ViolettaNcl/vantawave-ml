import numpy as np

from vantawave.ml.error_analysis.analyzer import analyze_errors


def test_error_analysis_counts_fp_and_fn():
    y = np.array([0, 0, 1, 1])
    scores = np.array([0.1, 0.8, 0.2, 0.9])
    result = analyze_errors(y, scores, threshold=0.5)
    assert result.false_positives == 1
    assert result.false_negatives == 1
    assert result.correct == 2
