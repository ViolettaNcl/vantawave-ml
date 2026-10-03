from dataclasses import asdict, dataclass
import time
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

@dataclass(frozen=True)
class BinaryMetrics:
    accuracy: float
    precision: float
    recall: float
    f1: float
    pr_auc: float | None
    roc_auc: float | None
    false_positive_rate: float
    false_negative_rate: float
    inference_ms_per_1000: float
    confusion_matrix: list[list[int]]

    def to_dict(self):
        return asdict(self)

def evaluate_binary_classifier(model, X, y) -> BinaryMetrics:
    started = time.perf_counter()
    predictions = model.predict(X)
    elapsed = time.perf_counter() - started

    scores = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        if getattr(proba, "ndim", 0) == 2 and proba.shape[1] >= 2:
            scores = proba[:, 1]
    elif hasattr(model, "decision_function"):
        scores = model.decision_function(X)

    matrix = confusion_matrix(y, predictions, labels=[0, 1])
    tn, fp, fn, tp = matrix.ravel()
    fpr = fp / (fp + tn) if fp + tn else 0.0
    fnr = fn / (fn + tp) if fn + tp else 0.0

    pr_auc = None
    roc_auc = None
    if scores is not None and len(np.unique(y)) == 2:
        pr_auc = float(average_precision_score(y, scores))
        roc_auc = float(roc_auc_score(y, scores))

    rows = max(len(X), 1)
    return BinaryMetrics(
        accuracy=float(accuracy_score(y, predictions)),
        precision=float(precision_score(y, predictions, zero_division=0)),
        recall=float(recall_score(y, predictions, zero_division=0)),
        f1=float(f1_score(y, predictions, zero_division=0)),
        pr_auc=pr_auc,
        roc_auc=roc_auc,
        false_positive_rate=float(fpr),
        false_negative_rate=float(fnr),
        inference_ms_per_1000=float(elapsed * 1000 * (1000 / rows)),
        confusion_matrix=matrix.astype(int).tolist(),
    )
