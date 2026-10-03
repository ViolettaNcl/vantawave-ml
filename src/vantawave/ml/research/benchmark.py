from __future__ import annotations

from pathlib import Path
import time
import joblib

from vantawave.ml.evaluation.metrics import evaluate_binary_classifier
from vantawave.ml.explainability.permutation import permutation_feature_importance
from vantawave.ml.research.models import build_awid3_models
from vantawave.reports.research import ModelEvaluation

def run_awid3_benchmark(
    split,
    *,
    artifact_dir: str | Path | None = None,
):
    artifact_dir = Path(artifact_dir) if artifact_dir else None
    if artifact_dir:
        artifact_dir.mkdir(parents=True, exist_ok=True)

    evaluations = []
    fitted = {}

    for name, model in build_awid3_models().items():
        started = time.perf_counter()
        model.fit(split.X_train, split.y_train)
        training_seconds = time.perf_counter() - started

        validation = evaluate_binary_classifier(
            model,
            split.X_validation,
            split.y_validation,
        )
        test = evaluate_binary_classifier(
            model,
            split.X_test,
            split.y_test,
        )

        artifact_path = None
        if artifact_dir:
            path = artifact_dir / f"{name}.joblib"
            joblib.dump(model, path)
            artifact_path = str(path)

        evaluations.append(
            ModelEvaluation(
                model=name,
                validation=validation.to_dict(),
                test=test.to_dict(),
                training_seconds=float(training_seconds),
                artifact_path=artifact_path,
            )
        )
        fitted[name] = model

    best = max(evaluations, key=lambda item: item.validation["f1"])
    best_model = fitted[best.model]
    importance = permutation_feature_importance(
        best_model,
        split.X_test,
        split.y_test,
        scoring="f1",
        repeats=3,
    )

    return evaluations, importance, best.model
