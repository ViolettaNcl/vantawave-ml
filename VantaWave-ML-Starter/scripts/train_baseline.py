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
    parser.add_argument("--out", type=Path, default=Path("artifacts/isolation_forest.joblib"))
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    X = select_features(df)

    detector = IsolationForestDetector().fit(X)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(detector, args.out)

    results = detector.predict(X)
    n_anomaly = sum(r.label == -1 for r in results)
    print(f"rows={len(results)} anomalies={n_anomaly} model={args.out}")

if __name__ == "__main__":
    main()
