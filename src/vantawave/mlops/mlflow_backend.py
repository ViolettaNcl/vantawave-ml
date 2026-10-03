from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class MLflowUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class MLflowConfig:
    tracking_uri: str
    experiment_name: str
    registry_name: str


def _require_mlflow():
    try:
        import mlflow
        from mlflow import MlflowClient
    except ImportError as exc:
        raise MLflowUnavailable(
            'MLflow is optional. Install it with: pip install -e ".[mlops]"'
        ) from exc
    return mlflow, MlflowClient



def sklearn_log_options(mlflow):
    return {
        "serialization_format": mlflow.sklearn.SERIALIZATION_FORMAT_SKOPS,
        "skops_trusted_types": ["numpy.dtype"],
    }


def configure_local_mlflow(
    *,
    root: str | Path = "artifacts/mlflow",
    experiment_name: str = "vantawave-awid3",
    registry_name: str = "VantaWave-AWID3",
) -> MLflowConfig:
    mlflow, _ = _require_mlflow()

    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    db_path = (root / "mlflow.db").resolve()
    tracking_uri = f"sqlite:///{db_path.as_posix()}"

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_registry_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)

    return MLflowConfig(
        tracking_uri=tracking_uri,
        experiment_name=experiment_name,
        registry_name=registry_name,
    )


def log_and_register_sklearn(
    model,
    *,
    model_name: str,
    metrics: dict,
    params: dict | None = None,
    tags: dict | None = None,
    alias: str | None = "candidate",
):
    mlflow, MlflowClient = _require_mlflow()
    client = MlflowClient()

    with mlflow.start_run() as run:
        if params:
            mlflow.log_params({k: str(v) for k, v in params.items()})
        if metrics:
            mlflow.log_metrics(
                {k: float(v) for k, v in metrics.items() if v is not None}
            )
        if tags:
            mlflow.set_tags({k: str(v) for k, v in tags.items()})

        mlflow.sklearn.log_model(
            sk_model=model,
            name="model",
            registered_model_name=model_name,
            **sklearn_log_options(mlflow),
        )

        versions = client.search_model_versions(f"name='{model_name}'")
        matching = [v for v in versions if getattr(v, "run_id", None) == run.info.run_id]
        if not matching:
            raise RuntimeError("MLflow registered model version could not be resolved.")

        version = max(matching, key=lambda item: int(item.version))
        if alias:
            client.set_registered_model_alias(
                name=model_name,
                alias=alias,
                version=version.version,
            )

        return {
            "run_id": run.info.run_id,
            "model_name": model_name,
            "version": int(version.version),
            "alias": alias,
        }


def promote_alias(
    *,
    model_name: str,
    version: int,
    alias: str = "champion",
):
    _, MlflowClient = _require_mlflow()
    client = MlflowClient()
    client.set_registered_model_alias(
        name=model_name,
        alias=alias,
        version=str(version),
    )
    return {
        "model_name": model_name,
        "version": int(version),
        "alias": alias,
    }
