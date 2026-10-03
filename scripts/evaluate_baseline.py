from __future__ import annotations
import argparse
from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

from vantawave.ml.features import select_features

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("artifacts/isolation_forest.joblib"),
    )
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    if "is_anomaly" not in df.columns:
        raise ValueError("Evaluation CSV must contain an 'is_anomaly' label column.")

    detector = joblib.load(args.model)
    X = select_features(df)

    results = detector.predict(X)
    y_true = df["is_anomaly"].astype(int).to_numpy()
    y_pred = [1 if r.label == -1 else 0 for r in results]

    print("Confusion matrix:")
    print(confusion_matrix(y_true, y_pred))
    print()
    print(classification_report(
        y_true,
        y_pred,
        target_names=["normal", "anomaly"],
        digits=4,
        zero_division=0,
    ))

if __name__ == "__main__":
    main()
