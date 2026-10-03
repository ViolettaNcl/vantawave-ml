from dataclasses import dataclass
import numpy as np
from sklearn.ensemble import IsolationForest

@dataclass(frozen=True)
class AnomalyResult:
    label: int
    anomaly_score: float

class IsolationForestDetector:
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=250,
        )

    def fit(self, X):
        self.model.fit(X)
        return self

    def predict(self, X) -> list[AnomalyResult]:
        labels = self.model.predict(X)
        scores = -np.asarray(self.model.decision_function(X))
        return [
            AnomalyResult(label=int(label), anomaly_score=float(score))
            for label, score in zip(labels, scores)
        ]
