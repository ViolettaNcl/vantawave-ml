from vantawave.monitoring.policy import recommend_retraining


def test_retraining_recommended_for_high_drift_and_bad_metrics():
    result = recommend_retraining(
        drift_findings=[
            {"severity": "high"},
            {"severity": "warning"},
        ],
        performance_metrics={
            "f1": 0.70,
            "false_positive_rate": 0.15,
        },
    )
    assert result.recommended
    assert result.priority == "high"
    assert len(result.reasons) >= 2


def test_retraining_not_recommended_when_stable():
    result = recommend_retraining(
        drift_findings=[{"severity": "ok"}],
        performance_metrics={
            "f1": 0.91,
            "false_positive_rate": 0.03,
        },
    )
    assert not result.recommended
