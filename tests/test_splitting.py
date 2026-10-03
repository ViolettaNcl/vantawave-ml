import pandas as pd
from vantawave.data.schema import FEATURE_COLUMNS, TARGET_COLUMN
from vantawave.data.splitting import stratified_split

def test_stratified_split_sizes():
    rows = []
    for i in range(200):
        row = {feature: float(i % 7) for feature in FEATURE_COLUMNS}
        row["rssi_mean"] = -50.0
        row[TARGET_COLUMN] = 1 if i % 10 == 0 else 0
        rows.append(row)
    split = stratified_split(pd.DataFrame(rows))
    assert len(split.train) == 140
    assert len(split.validation) == 30
    assert len(split.test) == 30
