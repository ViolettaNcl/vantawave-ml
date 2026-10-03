from __future__ import annotations
import argparse
from pathlib import Path
import joblib
import pandas as pd

from vantawave.ml.features import select_features
from vantawave.ml.detectors import IsolationForestDetector

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/isolation_forest.joblib"),
    )
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    X = select_features(df)

    # For the synthetic demo, train primarily on rows marked normal when labels exist.
    if "is_anomaly" in df.columns:
        X_train = X[df["is_anomaly"] == 0]
    else:
        X_train = X

    detector = IsolationForestDetector().fit(X_train)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(detector, args.out)

    results = detector.predict(X)
    n_anomaly = sum(r.label == -1 for r in results)

    print(f"training_rows={len(X_train)}")
    print(f"scored_rows={len(X)}")
    print(f"predicted_anomalies={n_anomaly}")
    print(f"model={args.out}")

if __name__ == "__main__":
    main()
