import pandas as pd

from vantawave.data.leakage import audit_exact_target_copies, audit_feature_names

def test_target_like_feature_name_is_flagged():
    findings = audit_feature_names(["frame.len", "attack_map"])
    assert len(findings) == 1
    assert findings[0].column == "attack_map"

def test_exact_target_copy_is_flagged():
    frame = pd.DataFrame(
        {
            "feature": [1, 0, 1],
            "is_anomaly": [1, 0, 1],
            "copied": [1, 0, 1],
        }
    )
    findings = audit_exact_target_copies(frame, "is_anomaly")
    assert any(item.column == "copied" for item in findings)
