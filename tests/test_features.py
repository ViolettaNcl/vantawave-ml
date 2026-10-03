import pandas as pd
import pytest
from vantawave.ml.features import DEFAULT_FEATURES, select_features

def make_frame():
    row = {name: 1.0 for name in DEFAULT_FEATURES}
    row["rssi_mean"] = -50.0
    return pd.DataFrame([row])

def test_select_features_accepts_complete_frame():
    assert list(select_features(make_frame()).columns) == DEFAULT_FEATURES

def test_select_features_rejects_missing_feature():
    with pytest.raises(ValueError):
        select_features(make_frame().drop(columns=[DEFAULT_FEATURES[0]]))
