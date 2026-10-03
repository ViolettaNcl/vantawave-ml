import pandas as pd
from vantawave.data.awid3 import AWID3_FEATURES
from vantawave.ml.research.splitting import stratified_research_split

def test_research_split_is_70_15_15():
    rows = []
    labels = []
    for i in range(200):
        row = {name: str(i % 3) for name in AWID3_FEATURES}
        row["frame.len"] = float(100 + i)
        row["radiotap.length"] = 48.0
        row["radiotap.dbm_antsignal"] = float(-120 - i % 10)
        row["wlan.duration"] = float(i % 50)
        rows.append(row)
        labels.append(1 if i % 10 == 0 else 0)

    split = stratified_research_split(pd.DataFrame(rows), pd.Series(labels))
    assert len(split.X_train) == 140
    assert len(split.X_validation) == 30
    assert len(split.X_test) == 30
    assert split.y_test.sum() > 0
