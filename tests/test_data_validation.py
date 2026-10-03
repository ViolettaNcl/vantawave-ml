import pandas as pd
from vantawave.data.schema import FEATURE_COLUMNS, TARGET_COLUMN
from vantawave.data.validation import validate_dataset

def valid_frame():
    row = {feature: 1.0 for feature in FEATURE_COLUMNS}
    row["rssi_mean"] = -50.0
    row[TARGET_COLUMN] = 0
    return pd.DataFrame([row, {**row, TARGET_COLUMN: 1, "auth_rate": 4.0}])

def test_valid_dataset_passes():
    assert validate_dataset(valid_frame()).is_valid

def test_missing_column_fails():
    report = validate_dataset(valid_frame().drop(columns=["auth_rate"]))
    assert not report.is_valid

def test_retry_ratio_bounds():
    frame = valid_frame()
    frame.loc[0, "retry_ratio"] = 1.5
    report = validate_dataset(frame)
    assert not report.is_valid
    assert any(issue.code == "out_of_bounds" for issue in report.issues)
