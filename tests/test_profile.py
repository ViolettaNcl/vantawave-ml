import pandas as pd
from vantawave.data.profile import profile_dataset

def test_profile_counts_rows_and_labels():
    frame = pd.DataFrame(
        {
            "x": [1, 2, 3],
            "kind": ["a", "a", "b"],
            "Label": ["Normal", "Normal", "Attack"],
        }
    )
    profile = profile_dataset(frame, "Label")
    assert profile.rows == 3
    assert profile.columns == 3
    assert profile.label_distribution["Normal"] == 2
