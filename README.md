# VantaWave ML

**Wi‑Fi Security & Machine Learning Research Platform**

VantaWave ML is an independent portfolio and learning project focused on
wireless-network telemetry, machine-learning anomaly detection, attack
classification, experiment tracking, and authorized security research on
networks owned by or explicitly permitted to the operator.

## Current version — v0.2

Implemented:

- clean Python package structure;
- FastAPI application;
- `/` project landing endpoint;
- `/health` health check;
- authorized-lab target validation;
- Wi‑Fi-oriented feature schema;
- Isolation Forest anomaly-detection baseline;
- reproducible synthetic demo dataset generator;
- baseline training script;
- baseline evaluation script;
- pytest test suite.

## Quick start

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m pytest
python -m uvicorn vantawave.api.main:app --reload
```

Open:

- API root: http://127.0.0.1:8000/
- Swagger UI: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Run the ML demo

Generate a reproducible demo dataset:

```powershell
python scripts/generate_demo_data.py
```

Train the Isolation Forest baseline:

```powershell
python scripts/train_baseline.py data/demo/wifi_events.csv
```

Evaluate it:

```powershell
python scripts/evaluate_baseline.py data/demo/wifi_events.csv
```

This demo dataset is synthetic and exists only to validate the complete ML
pipeline. It must not be presented as evidence of real-world Wi‑Fi detection
performance.

## Planned roadmap

1. Real public Wi‑Fi intrusion dataset adapter.
2. Data validation and leakage checks.
3. Logistic Regression / Random Forest / CatBoost comparison.
4. Experiment tracking with MLflow.
5. Live passive Wi‑Fi telemetry adapter.
6. Authorized laboratory experiment mode.
7. Dashboard and incident timeline.
8. Deep anomaly detection with PyTorch.
9. AI incident explanation from measured evidence.

## Project scope

VantaWave ML is designed for defensive research and authorized experiments.
Active lab functionality must be restricted to explicitly registered test
equipment.

No third-party source code is bundled in this starter release.
External libraries and research datasets remain subject to their respective
licenses and attribution requirements.
