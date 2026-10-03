from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path("data/demo/wifi_events.csv")
SEED = 42

def main():
    rng = np.random.default_rng(SEED)
    normal_n = 950
    anomaly_n = 50

    normal = pd.DataFrame({
        "auth_rate": rng.normal(2.0, 0.5, normal_n).clip(0),
        "assoc_rate": rng.normal(1.5, 0.4, normal_n).clip(0),
        "deauth_rate": rng.normal(0.15, 0.08, normal_n).clip(0),
        "beacon_rate": rng.normal(10.0, 1.0, normal_n).clip(0),
        "unique_clients": rng.integers(2, 9, normal_n),
        "unique_bssids": rng.integers(1, 3, normal_n),
        "rssi_mean": rng.normal(-52, 6, normal_n),
        "rssi_std": rng.normal(3.5, 1.0, normal_n).clip(0.1),
        "retry_ratio": rng.normal(0.08, 0.03, normal_n).clip(0, 1),
        "event_rate": rng.normal(120, 20, normal_n).clip(1),
        "is_anomaly": 0,
    })

    anomaly = pd.DataFrame({
        "auth_rate": rng.normal(16, 4, anomaly_n).clip(0),
        "assoc_rate": rng.normal(8, 2, anomaly_n).clip(0),
        "deauth_rate": rng.normal(11, 3, anomaly_n).clip(0),
        "beacon_rate": rng.normal(18, 4, anomaly_n).clip(0),
        "unique_clients": rng.integers(8, 25, anomaly_n),
        "unique_bssids": rng.integers(2, 7, anomaly_n),
        "rssi_mean": rng.normal(-67, 8, anomaly_n),
        "rssi_std": rng.normal(10, 3, anomaly_n).clip(0.1),
        "retry_ratio": rng.normal(0.42, 0.12, anomaly_n).clip(0, 1),
        "event_rate": rng.normal(430, 80, anomaly_n).clip(1),
        "is_anomaly": 1,
    })

    df = pd.concat([normal, anomaly], ignore_index=True)
    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Created {OUT} with {len(df)} rows.")
    print(df["is_anomaly"].value_counts().sort_index().rename(index={0: "normal", 1: "anomaly"}))

if __name__ == "__main__":
    main()
