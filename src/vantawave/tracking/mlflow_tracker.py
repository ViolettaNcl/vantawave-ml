from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path

class MLflowUnavailable(RuntimeError):
    pass

class MLflowTracker:
    def __init__(self, experiment_name: str = "vantawave-awid3"):
        try:
            import mlflow
        except ImportError as exc:
            raise MLflowUnavailable(
                'MLflow is optional. Install it with: pip install -e ".[research]"'
            ) from exc
        self.mlflow = mlflow
        self.experiment_name = experiment_name
        self.mlflow.set_experiment(experiment_name)

    @contextmanager
    def run(self, run_name: str):
        with self.mlflow.start_run(run_name=run_name):
            yield self

    def log_params(self, params: dict):
        self.mlflow.log_params(params)

    def log_metrics(self, metrics: dict):
        safe = {k: float(v) for k, v in metrics.items() if v is not None}
        self.mlflow.log_metrics(safe)

    def log_artifact(self, path: str | Path):
        self.mlflow.log_artifact(str(path))
