from __future__ import annotations
from dataclasses import dataclass
from sklearn.ensemble import IsolationForest
import numpy as np

@dataclass
class AnomalyResult:
    label: int
    anomaly_score: float

class IsolationForestDetector:
    def __init__(self, contamination: float = 0.03, random_state: int = 42):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
        )

    def fit(self, X):
        self.model.fit(X)
        return self

    def predict(self, X) -> list[AnomalyResult]:
        labels = self.model.predict(X)
        raw = self.model.decision_function(X)
        # Larger score means "more anomalous" for the UI.
        scores = -np.asarray(raw)
        return [
            AnomalyResult(label=int(label), anomaly_score=float(score))
            for label, score in zip(labels, scores)
        ]
