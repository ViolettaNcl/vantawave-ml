from __future__ import annotations

from dataclasses import asdict, dataclass
import numpy as np


class SHAPUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class SHAPFeature:
    feature: str
    mean_abs_shap: float

    def to_dict(self):
        return asdict(self)


def is_shap_available() -> bool:
    try:
        import shap  # noqa: F401
    except ImportError:
        return False
    return True


def explain_tree_pipeline(
    pipeline,
    X,
    *,
    max_rows: int = 500,
    top_n: int = 20,
) -> list[SHAPFeature]:
    try:
        import shap
    except ImportError as exc:
        raise SHAPUnavailable(
            'SHAP is optional. Install it with: pip install -e ".[explain]"'
        ) from exc

    if not hasattr(pipeline, "named_steps"):
        raise TypeError("Expected a scikit-learn Pipeline.")

    preprocess = pipeline.named_steps.get("preprocess")
    model = pipeline.named_steps.get("model")
    if preprocess is None or model is None:
        raise ValueError("Pipeline must expose 'preprocess' and 'model' steps.")

    sample = X.iloc[:max_rows].copy()
    transformed = preprocess.transform(sample)

    if hasattr(preprocess, "get_feature_names_out"):
        feature_names = [str(x) for x in preprocess.get_feature_names_out()]
    else:
        feature_names = [f"feature_{i}" for i in range(transformed.shape[1])]

    explainer = shap.TreeExplainer(model)
    explanation = explainer(transformed)
    values = np.asarray(explanation.values)

    if values.ndim == 3:
        # Binary/multiclass classifiers may return a class dimension.
        class_index = 1 if values.shape[-1] > 1 else 0
        values = values[:, :, class_index]
    if values.ndim != 2:
        raise ValueError(f"Unexpected SHAP values shape: {values.shape}")

    importance = np.mean(np.abs(values), axis=0)
    items = [
        SHAPFeature(feature=name, mean_abs_shap=float(value))
        for name, value in zip(feature_names, importance)
    ]
    return sorted(items, key=lambda x: x.mean_abs_shap, reverse=True)[:top_n]
