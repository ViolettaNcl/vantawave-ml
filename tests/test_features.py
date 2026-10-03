import pandas as pd
import pytest
from vantawave.ml.features import DEFAULT_FEATURES, select_features

def make_frame():
    return pd.DataFrame([{name: 1.0 for name in DEFAULT_FEATURES}])

def test_select_features_accepts_complete_frame():
    result = select_features(make_frame())
    assert list(result.columns) == DEFAULT_FEATURES

def test_select_features_rejects_missing_feature():
    frame = make_frame().drop(columns=[DEFAULT_FEATURES[0]])
    with pytest.raises(ValueError):
        select_features(frame)
