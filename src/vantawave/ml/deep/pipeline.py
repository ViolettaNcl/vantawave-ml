from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split

from vantawave.data.awid3 import load_awid3_frame
from vantawave.ml.deep.autoencoder import AutoencoderConfig, build_autoencoder
from vantawave.ml.deep.scoring import (
    calibrate_reconstruction_threshold,
    evaluate_anomaly_scores,
    reconstruction_errors,
)
from vantawave.ml.deep.training import TrainingConfig, train_autoencoder
from vantawave.ml.research.preprocessing import build_awid3_preprocessor


@dataclass(frozen=True)
class DeepSplit:
    train_normal: pd.DataFrame
    validation_normal: pd.DataFrame
    test_normal: pd.DataFrame
    test_anomalies: pd.DataFrame
    anomaly_labels: pd.Series


def make_normal_only_split(
    features: pd.DataFrame,
    binary_target: pd.Series,
    raw_labels: pd.Series,
    *,
    random_state: int = 42,
) -> DeepSplit:
    normal_mask = binary_target.to_numpy() == 0
    anomaly_mask = ~normal_mask

    normal = features.loc[normal_mask].reset_index(drop=True)
    anomalies = features.loc[anomaly_mask].reset_index(drop=True)
    anomaly_labels = raw_labels.loc[anomaly_mask].reset_index(drop=True)

    if len(normal) < 20:
        raise ValueError("At least 20 normal rows are required.")
    if len(anomalies) < 1:
        raise ValueError("At least one anomaly row is required.")

    train_normal, temp = train_test_split(
        normal,
        test_size=0.30,
        random_state=random_state,
    )
    validation_normal, test_normal = train_test_split(
        temp,
        test_size=0.50,
        random_state=random_state,
    )

    return DeepSplit(
        train_normal=train_normal.reset_index(drop=True),
        validation_normal=validation_normal.reset_index(drop=True),
        test_normal=test_normal.reset_index(drop=True),
        test_anomalies=anomalies,
        anomaly_labels=anomaly_labels,
    )


def _combine_test(split: DeepSplit, preprocessor):
    normal = preprocessor.transform(split.test_normal)
    anomalies = preprocessor.transform(split.test_anomalies)
    X = np.vstack([normal, anomalies]).astype(np.float32)
    y = np.concatenate(
        [
            np.zeros(len(normal), dtype=int),
            np.ones(len(anomalies), dtype=int),
        ]
    )
    raw_labels = pd.Series(
        ["Normal"] * len(normal) + split.anomaly_labels.astype(str).tolist(),
        dtype="string",
    )
    return X, y, raw_labels


def _attack_recall(raw_labels, scores, threshold: float, known_labels: set[str]):
    raw_labels = pd.Series(raw_labels, dtype="string")
    scores = np.asarray(scores, dtype=float)

    by_label = {}
    for label in sorted(set(raw_labels.tolist())):
        if label.lower() == "normal":
            continue
        mask = raw_labels.to_numpy() == label
        recall = float((scores[mask] >= threshold).mean()) if mask.any() else 0.0
        by_label[label] = {
            "rows": int(mask.sum()),
            "recall": recall,
            "category": "known" if label in known_labels else "unknown",
        }

    known_mask = raw_labels.isin(list(known_labels)).to_numpy()
    unknown_mask = (~raw_labels.isin(list(known_labels)) & (raw_labels.str.lower() != "normal")).to_numpy()

    def grouped(mask):
        return {
            "rows": int(mask.sum()),
            "recall": float((scores[mask] >= threshold).mean()) if mask.any() else None,
        }

    return {
        "by_attack_label": by_label,
        "known_attacks": grouped(known_mask),
        "unknown_attacks": grouped(unknown_mask),
    }


def _isolation_forest_baseline(X_train, X_validation_normal, X_test, y_test, raw_labels, known_labels):
    model = IsolationForest(
        n_estimators=300,
        contamination="auto",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train)

    validation_scores = -model.decision_function(X_validation_normal)
    threshold = float(np.quantile(validation_scores, 0.99))
    test_scores = -model.decision_function(X_test)
    metrics = evaluate_anomaly_scores(y_test, test_scores, threshold)

    return model, {
        "threshold": threshold,
        "metrics": metrics.to_dict(),
        "attack_recall": _attack_recall(
            raw_labels,
            test_scores,
            threshold,
            known_labels,
        ),
    }


def run_deep_anomaly_research(
    raw_frame: pd.DataFrame,
    *,
    label_column: str | None = None,
    output_dir: str | Path = "artifacts/v06",
    known_attack_labels: set[str] | None = None,
    training_config: TrainingConfig | None = None,
) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_dir = output_dir / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    known_attack_labels = known_attack_labels or {"Deauth"}
    prepared = load_awid3_frame(raw_frame, label_column=label_column)
    split = make_normal_only_split(
        prepared.features,
        prepared.binary_target,
        prepared.raw_labels,
    )

    preprocessor = build_awid3_preprocessor()
    preprocessor.fit(split.train_normal)

    X_train = np.asarray(preprocessor.transform(split.train_normal), dtype=np.float32)
    X_validation_normal = np.asarray(
        preprocessor.transform(split.validation_normal),
        dtype=np.float32,
    )
    X_test, y_test, raw_test_labels = _combine_test(split, preprocessor)

    model = build_autoencoder(
        input_dim=X_train.shape[1],
        config=AutoencoderConfig(
            latent_dim=max(4, min(12, X_train.shape[1] // 3)),
            hidden_dim=max(16, min(64, X_train.shape[1] * 2)),
            dropout=0.05,
            seed=42,
        ),
    )
    model, history, device = train_autoencoder(
        model,
        X_train,
        X_validation_normal,
        config=training_config or TrainingConfig(),
    )

    validation_errors = reconstruction_errors(
        model,
        X_validation_normal,
        device=device,
    )
    threshold = calibrate_reconstruction_threshold(
        validation_errors,
        quantile=0.99,
    )

    test_errors = reconstruction_errors(model, X_test, device=device)
    metrics = evaluate_anomaly_scores(y_test, test_errors, threshold)
    attack_recall = _attack_recall(
        raw_test_labels,
        test_errors,
        threshold,
        known_attack_labels,
    )

    torch, _ = __import__("vantawave.ml.deep.autoencoder", fromlist=["require_torch"]).require_torch()
    autoencoder_path = model_dir / "autoencoder_state.pt"
    torch.save(
        {
            "state_dict": model.state_dict(),
            "input_dim": int(X_train.shape[1]),
            "threshold": float(threshold),
            "project_version": "0.6.0",
        },
        autoencoder_path,
    )
    joblib.dump(preprocessor, model_dir / "preprocessor.joblib")

    isolation_model, isolation = _isolation_forest_baseline(
        X_train,
        X_validation_normal,
        X_test,
        y_test,
        raw_test_labels,
        known_attack_labels,
    )
    joblib.dump(isolation_model, model_dir / "isolation_forest.joblib")

    payload = {
        "project_version": "0.6.0",
        "task": "normal-only-deep-anomaly-detection",
        "known_attack_labels": sorted(known_attack_labels),
        "split": {
            "train_normal": len(split.train_normal),
            "validation_normal": len(split.validation_normal),
            "test_normal": len(split.test_normal),
            "test_anomalies": len(split.test_anomalies),
        },
        "transformed_feature_count": int(X_train.shape[1]),
        "autoencoder": {
            "device": device,
            "threshold_method": "validation-normal-99th-percentile",
            "threshold": float(threshold),
            "metrics": metrics.to_dict(),
            "attack_recall": attack_recall,
            "training": history.to_dict(),
            "artifact": str(autoencoder_path),
        },
        "isolation_forest": isolation,
        "comparison": {
            "autoencoder_f1": metrics.f1,
            "isolation_forest_f1": isolation["metrics"]["f1"],
            "autoencoder_unknown_recall": attack_recall["unknown_attacks"]["recall"],
            "isolation_forest_unknown_recall": isolation["attack_recall"]["unknown_attacks"]["recall"],
        },
    }

    report = output_dir / "deep_anomaly_report.json"
    report.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload
