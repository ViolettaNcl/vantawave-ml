from __future__ import annotations

from pathlib import Path
from vantawave.mlops.mlflow_backend import MLflowUnavailable, configure_local_mlflow


def main():
    try:
        config = configure_local_mlflow(root=Path("artifacts/v05/mlflow"))
    except MLflowUnavailable as exc:
        print(exc)
        raise SystemExit(2)

    print("VantaWave ML local MLflow configuration")
    print(f"tracking URI: {config.tracking_uri}")
    print(f"experiment: {config.experiment_name}")
    print(f"registry model: {config.registry_name}")
    print()
    print("To launch the UI/server on port 5000:")
    print(
        "python -m mlflow server "
        f'--backend-store-uri "{config.tracking_uri}" '
        '--host 127.0.0.1 --port 5000'
    )


if __name__ == "__main__":
    main()
