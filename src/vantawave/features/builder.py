import pandas as pd
from vantawave.data.schema import FEATURE_COLUMNS

def build_feature_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in FEATURE_COLUMNS if c not in frame.columns]
    if missing:
        raise ValueError(f"Missing required features: {missing}")
    features = frame[FEATURE_COLUMNS].copy()
    if features.isna().any().any():
        raise ValueError("Feature matrix contains missing values.")
    non_numeric = [c for c in features.columns if not pd.api.types.is_numeric_dtype(features[c])]
    if non_numeric:
        raise ValueError(f"Non-numeric features detected: {non_numeric}")
    return features
