from __future__ import annotations

from dataclasses import asdict, dataclass
import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix


@dataclass(frozen=True)
class ThresholdCandidate:
    threshold: float
    precision: float
    recall: float
    f1: float
    false_positive_rate: float

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class ThresholdResult:
    threshold: float
    objective: str
    validation: ThresholdCandidate
    evaluated_candidates: int

    def to_dict(self):
        return {
            "threshold": self.threshold,
            "objective": self.objective,
            "validation": self.validation.to_dict(),
            "evaluated_candidates": self.evaluated_candidates,
        }


def positive_scores(model, X) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        if getattr(proba, "ndim", 0) == 2 and proba.shape[1] >= 2:
            return np.asarray(proba[:, 1], dtype=float)
    if hasattr(model, "decision_function"):
        raw = np.asarray(model.decision_function(X), dtype=float)
        return 1.0 / (1.0 + np.exp(-raw))
    raise TypeError("Model does not expose predict_proba or decision_function.")


def score_threshold(y_true, scores, threshold: float) -> ThresholdCandidate:
    predictions = (np.asarray(scores) >= threshold).astype(int)
    matrix = confusion_matrix(y_true, predictions, labels=[0, 1])
    tn, fp, fn, tp = matrix.ravel()
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return ThresholdCandidate(
        threshold=float(threshold),
        precision=float(precision_score(y_true, predictions, zero_division=0)),
        recall=float(recall_score(y_true, predictions, zero_division=0)),
        f1=float(f1_score(y_true, predictions, zero_division=0)),
        false_positive_rate=float(fpr),
    )


def calibrate_threshold(
    y_true,
    scores,
    *,
    objective: str = "f1",
    min_precision: float = 0.0,
    max_false_positive_rate: float = 1.0,
    thresholds=None,
) -> ThresholdResult:
    if objective not in {"f1", "recall", "precision"}:
        raise ValueError("objective must be one of: f1, recall, precision")

    thresholds = (
        np.asarray(thresholds, dtype=float)
        if thresholds is not None
        else np.linspace(0.05, 0.95, 91)
    )

    candidates = [
        score_threshold(y_true, scores, float(t))
        for t in thresholds
    ]
    feasible = [
        item for item in candidates
        if item.precision >= min_precision
        and item.false_positive_rate <= max_false_positive_rate
    ]
    if not feasible:
        raise ValueError("No threshold satisfies the supplied constraints.")

    def key(item: ThresholdCandidate):
        primary = getattr(item, objective)
        return (
            primary,
            item.f1,
            item.recall,
            -item.false_positive_rate,
            -abs(item.threshold - 0.5),
        )

    best = max(feasible, key=key)
    return ThresholdResult(
        threshold=best.threshold,
        objective=objective,
        validation=best,
        evaluated_candidates=len(candidates),
    )
