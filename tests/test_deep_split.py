import pandas as pd

from vantawave.data.awid3 import AWID3_FEATURES
from vantawave.ml.deep.pipeline import make_normal_only_split


def test_normal_only_split_excludes_anomalies_from_training():
    rows = []
    target = []
    labels = []

    for i in range(120):
        row = {feature: str(i % 3) for feature in AWID3_FEATURES}
        row["frame.len"] = float(100 + i)
        row["radiotap.length"] = 48.0
        row["radiotap.dbm_antsignal"] = float(-100 - i % 10)
        row["wlan.duration"] = float(i % 50)
        rows.append(row)
        is_attack = i >= 100
        target.append(1 if is_attack else 0)
        labels.append("Deauth" if is_attack else "Normal")

    split = make_normal_only_split(
        pd.DataFrame(rows),
        pd.Series(target),
        pd.Series(labels),
    )

    assert len(split.test_anomalies) == 20
    assert set(split.anomaly_labels.unique()) == {"Deauth"}
    assert len(split.train_normal) + len(split.validation_normal) + len(split.test_normal) == 100
