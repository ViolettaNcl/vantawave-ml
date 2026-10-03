from __future__ import annotations

from dataclasses import asdict, dataclass
import numpy as np
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from vantawave.ml.deep.autoencoder import require_torch


def reconstruction_errors(model, X, *, device: str = "cpu") -> np.ndarray:
    torch, _ = require_torch()
    X = np.asarray(X, dtype=np.float32)
    tensor = torch.tensor(X, dtype=torch.float32, device=device)

    model.eval()
    with torch.no_grad():
        reconstructed = model(tensor)
        errors = torch.mean((reconstructed - tensor) ** 2, dim=1)

    return errors.detach().cpu().numpy().astype(float)


def calibrate_reconstruction_threshold(
    normal_validation_errors,
    *,
    quantile: float = 0.99,
) -> float:
    errors = np.asarray(normal_validation_errors, dtype=float)
    if not 0.5 <= quantile < 1.0:
        raise ValueError("quantile must be in [0.5, 1.0).")
    if errors.size == 0:
        raise ValueError("At least one validation error is required.")
    return float(np.quantile(errors, quantile))


@dataclass(frozen=True)
class AnomalyMetrics:
    threshold: float
    precision: float
    recall: float
    f1: float
    false_positive_rate: float
    false_negative_rate: float
    pr_auc: float
    roc_auc: float
    confusion_matrix: list[list[int]]

    def to_dict(self):
        return asdict(self)


def evaluate_anomaly_scores(y_true, scores, threshold: float) -> AnomalyMetrics:
    y_true = np.asarray(y_true, dtype=int)
    scores = np.asarray(scores, dtype=float)
    predictions = (scores >= threshold).astype(int)

    matrix = confusion_matrix(y_true, predictions, labels=[0, 1])
    tn, fp, fn, tp = matrix.ravel()

    return AnomalyMetrics(
        threshold=float(threshold),
        precision=float(precision_score(y_true, predictions, zero_division=0)),
        recall=float(recall_score(y_true, predictions, zero_division=0)),
        f1=float(f1_score(y_true, predictions, zero_division=0)),
        false_positive_rate=float(fp / (fp + tn) if fp + tn else 0.0),
        false_negative_rate=float(fn / (fn + tp) if fn + tp else 0.0),
        pr_auc=float(average_precision_score(y_true, scores)),
        roc_auc=float(roc_auc_score(y_true, scores)),
        confusion_matrix=matrix.astype(int).tolist(),
    )
