from dataclasses import asdict, dataclass
from pathlib import Path
import json
import time
import joblib

from vantawave.data.schema import TARGET_COLUMN
from vantawave.features.builder import build_feature_matrix
from vantawave.ml.classification.baselines import build_baseline_models
from vantawave.ml.evaluation.metrics import BinaryMetrics, evaluate_binary_classifier

@dataclass
class BenchmarkEntry:
    model: str
    training_seconds: float
    metrics: BinaryMetrics
    artifact_path: str | None = None

    def to_dict(self):
        return asdict(self)

def run_benchmark(train_frame, validation_frame, artifact_dir: str | Path | None = None):
    artifact_path = Path(artifact_dir) if artifact_dir else None
    if artifact_path:
        artifact_path.mkdir(parents=True, exist_ok=True)

    X_train = build_feature_matrix(train_frame)
    y_train = train_frame[TARGET_COLUMN].astype(int)
    X_val = build_feature_matrix(validation_frame)
    y_val = validation_frame[TARGET_COLUMN].astype(int)

    results = []
    for name, model in build_baseline_models().items():
        started = time.perf_counter()
        model.fit(X_train, y_train)
        training_seconds = time.perf_counter() - started
        metrics = evaluate_binary_classifier(model, X_val, y_val)

        model_path = None
        if artifact_path:
            model_file = artifact_path / f"{name}.joblib"
            joblib.dump(model, model_file)
            model_path = str(model_file)

        results.append(BenchmarkEntry(
            model=name,
            training_seconds=float(training_seconds),
            metrics=metrics,
            artifact_path=model_path,
        ))

    return results

def save_benchmark_report(entries, path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"models": [entry.to_dict() for entry in entries]}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
