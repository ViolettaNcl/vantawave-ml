from __future__ import annotations
from dataclasses import asdict, dataclass

from sklearn.inspection import permutation_importance

@dataclass(frozen=True)
class FeatureImportance:
    feature: str
    importance_mean: float
    importance_std: float

    def to_dict(self):
        return asdict(self)

def permutation_feature_importance(
    model,
    X,
    y,
    *,
    scoring: str = "f1",
    repeats: int = 5,
    random_state: int = 42,
) -> list[FeatureImportance]:
    result = permutation_importance(
        model,
        X,
        y,
        scoring=scoring,
        n_repeats=repeats,
        random_state=random_state,
        n_jobs=1,
    )
    items = [
        FeatureImportance(
            feature=str(feature),
            importance_mean=float(mean),
            importance_std=float(std),
        )
        for feature, mean, std in zip(X.columns, result.importances_mean, result.importances_std)
    ]
    return sorted(items, key=lambda item: item.importance_mean, reverse=True)
