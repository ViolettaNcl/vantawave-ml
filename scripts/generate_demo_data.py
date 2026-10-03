from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path("data/demo/wifi_events.csv")
SEED = 42

def main():
    rng = np.random.default_rng(SEED)
    normal_n = 1900
    anomaly_n = 100

    normal = pd.DataFrame({
        "auth_rate": rng.normal(2.2, 0.7, normal_n).clip(0),
        "assoc_rate": rng.normal(1.6, 0.5, normal_n).clip(0),
        "deauth_rate": rng.normal(0.2, 0.12, normal_n).clip(0),
        "beacon_rate": rng.normal(10.0, 1.3, normal_n).clip(0),
        "unique_clients": rng.integers(2, 10, normal_n),
        "unique_bssids": rng.integers(1, 3, normal_n),
        "rssi_mean": rng.normal(-53, 7, normal_n),
        "rssi_std": rng.normal(3.8, 1.2, normal_n).clip(0.1),
        "retry_ratio": rng.normal(0.09, 0.04, normal_n).clip(0, 1),
        "event_rate": rng.normal(125, 28, normal_n).clip(1),
        "is_anomaly": 0,
    })

    anomaly = pd.DataFrame({
        "auth_rate": rng.normal(11.5, 5.0, anomaly_n).clip(0),
        "assoc_rate": rng.normal(6.5, 2.8, anomaly_n).clip(0),
        "deauth_rate": rng.normal(7.5, 4.0, anomaly_n).clip(0),
        "beacon_rate": rng.normal(15.5, 5.0, anomaly_n).clip(0),
        "unique_clients": rng.integers(6, 24, anomaly_n),
        "unique_bssids": rng.integers(2, 7, anomaly_n),
        "rssi_mean": rng.normal(-63, 10, anomaly_n),
        "rssi_std": rng.normal(8.0, 3.5, anomaly_n).clip(0.1),
        "retry_ratio": rng.normal(0.32, 0.16, anomaly_n).clip(0, 1),
        "event_rate": rng.normal(330, 120, anomaly_n).clip(1),
        "is_anomaly": 1,
    })

    df = pd.concat([normal, anomaly], ignore_index=True)
    df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)
    df.insert(0, "session_id", [f"demo-{i // 50:04d}" for i in range(len(df))])
    df.insert(0, "source", "synthetic-demo")
    df.insert(
        0,
        "timestamp",
        pd.date_range("2026-01-01", periods=len(df), freq="s", tz="UTC").astype(str),
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Created {OUT} with {len(df)} rows.")
    print(df["is_anomaly"].value_counts().sort_index().rename(index={0: "normal", 1: "anomaly"}))

if __name__ == "__main__":
    main()
