from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

from vantawave.data.awid3 import (
    AWID3_CATEGORICAL_FEATURES,
    AWID3_NUMERIC_FEATURES,
)

def build_awid3_preprocessor() -> ColumnTransformer:
    numeric = Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", MinMaxScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                    min_frequency=2,
                ),
            ),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric, AWID3_NUMERIC_FEATURES),
            ("categorical", categorical, AWID3_CATEGORICAL_FEATURES),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )
