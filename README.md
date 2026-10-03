# VantaWave ML

**End-to-end Wi‑Fi Security, Machine Learning & AI Research Platform**

VantaWave ML is an independent portfolio and learning project for building a
measurable ML security pipeline: data ingestion, validation, feature
engineering, supervised classification, anomaly detection, experiment
tracking, incident/risk analysis, APIs, and later passive Wi‑Fi telemetry,
MLOps, explainability, RAG, and a SOC-style dashboard.

## v0.3 — Data & ML Core

Implemented:

- CSV and optional Parquet dataset loader;
- explicit Wi‑Fi feature schema;
- dataset quality validation;
- duplicate/missing/bounds checks;
- class-imbalance warnings;
- stratified train/validation/test splitting;
- Logistic Regression baseline;
- Random Forest baseline;
- Histogram Gradient Boosting baseline;
- optional CatBoost adapter;
- Isolation Forest anomaly detection;
- reusable binary classification metrics;
- automatic model benchmark;
- model artifact saving;
- JSON benchmark reports;
- file-based experiment tracking foundation;
- transparent Incident/Risk Engine;
- expanded FastAPI endpoints;
- GitHub Actions CI;
- architecture/data/ML/evaluation/limitations docs;
- expanded automated test suite.

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m pytest
```

## Generate demo data

```powershell
python scripts/generate_demo_data.py
```

## Validate a dataset

```powershell
python scripts/validate_dataset.py data/demo/wifi_events.csv
```

## Run the model benchmark

```powershell
python scripts/train_benchmark.py data/demo/wifi_events.csv
```

Benchmark artifacts are written under `artifacts/benchmark/`.

## Start the API

```powershell
python -m uvicorn vantawave.api.main:app --reload
```

Useful endpoints:

- `/`
- `/health`
- `/features`
- `/models`
- `/risk/score`
- `/docs`

## Important limitation

The bundled demo generator is synthetic. Its metrics validate the software
pipeline only and must not be presented as real-world Wi‑Fi detection
performance.

The next major release replaces demo-only evaluation with a public research
dataset adapter and dataset-specific preprocessing.
