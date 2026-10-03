import pandas as pd
from sklearn.linear_model import LogisticRegression

from vantawave.ml.explainability.permutation import permutation_feature_importance

def test_permutation_importance_returns_ranked_features():
    X = pd.DataFrame(
        {
            "signal": [0, 0, 0, 1, 1, 1, 0, 1, 0, 1],
            "noise": [1, 0, 1, 0, 1, 0, 1, 0, 0, 1],
        }
    )
    y = pd.Series([0, 0, 0, 1, 1, 1, 0, 1, 0, 1])
    model = LogisticRegression().fit(X, y)
    items = permutation_feature_importance(model, X, y, repeats=2)
    assert len(items) == 2
    assert items[0].importance_mean >= items[1].importance_mean
