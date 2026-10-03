from __future__ import annotations
import pandas as pd

DEFAULT_FEATURES = [
    "auth_rate",
    "assoc_rate",
    "deauth_rate",
    "beacon_rate",
    "unique_clients",
    "unique_bssids",
    "rssi_mean",
    "rssi_std",
    "retry_ratio",
    "event_rate",
]

def select_features(frame: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in DEFAULT_FEATURES if c not in frame.columns]
    if missing:
        raise ValueError(f"Missing required features: {missing}")

    result = frame[DEFAULT_FEATURES].copy()

    if result.isnull().any().any():
        raise ValueError("Feature matrix contains missing values.")

    return result
