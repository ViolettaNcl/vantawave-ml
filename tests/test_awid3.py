import pandas as pd
import pytest

from vantawave.data.awid3 import (
    AWID3_CATEGORICAL_FEATURES,
    AWID3_FEATURES,
    AWID3_NUMERIC_FEATURES,
    detect_label_column,
    load_awid3_frame,
    normalize_awid3_columns,
)

def make_awid3_frame():
    rows = []
    for i in range(20):
        row = {
            "frame.len": 100 + i,
            "radiotap.length": 48,
            "radiotap.dbm_antsignal": -120 - i,
            "wlan.duration": 20 + i,
            "radiotap.present.tsft": "1-0-0",
            "radiotap.channel.freq": "2412",
            "radiotap.channel.type.cck": "1",
            "radiotap.channel.type.ofdm": "0",
            "wlan.fc.type": "0",
            "wlan.fc.subtype": str(i % 4),
            "wlan.fc.ds": "0",
            "wlan.fc.frag": "0",
            "wlan.fc.retry": "0",
            "wlan.fc.pwrmgt": "0",
            "wlan.fc.moredata": "0",
            "wlan.fc.protected": "1",
            "Label": "Normal" if i < 15 else "Deauth",
        }
        rows.append(row)
    return pd.DataFrame(rows)

def test_detect_label_column():
    assert detect_label_column(make_awid3_frame().columns) == "Label"

def test_load_awid3_binary_mapping():
    dataset = load_awid3_frame(make_awid3_frame())
    assert list(dataset.features.columns) == AWID3_FEATURES
    assert dataset.binary_target.sum() == 5
    assert len(dataset.binary_target) == 20

def test_alias_normalization():
    frame = make_awid3_frame().rename(columns={"radiotap.length": "radiotap.len"})
    normalized = normalize_awid3_columns(frame)
    assert "radiotap.length" in normalized.columns

def test_missing_feature_rejected():
    frame = make_awid3_frame().drop(columns=["wlan.fc.retry"])
    with pytest.raises(ValueError):
        load_awid3_frame(frame)

def test_feature_partition_is_complete():
    assert set(AWID3_NUMERIC_FEATURES + AWID3_CATEGORICAL_FEATURES) == set(AWID3_FEATURES)
