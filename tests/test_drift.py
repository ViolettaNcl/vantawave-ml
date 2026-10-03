import pandas as pd

from vantawave.ml.drift.baseline import build_drift_baseline, compare_to_baseline


def test_drift_baseline_detects_numeric_shift():
    reference = pd.DataFrame(
        {
            "signal": [0.0, 0.1, -0.1, 0.05, -0.05],
            "channel": ["a", "a", "b", "a", "b"],
        }
    )
    baseline = build_drift_baseline(reference)

    current = pd.DataFrame(
        {
            "signal": [3.0, 3.1, 2.9],
            "channel": ["c", "c", "c"],
        }
    )
    findings = compare_to_baseline(baseline, current)
    by_feature = {item.feature: item for item in findings}

    assert by_feature["signal"].severity == "high"
    assert by_feature["channel"].severity in {"warning", "high"}
