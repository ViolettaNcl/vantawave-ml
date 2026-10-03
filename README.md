# VantaWave ML

**End-to-end Wi‑Fi Security, Machine Learning & AI Research Platform**

VantaWave ML is an independent portfolio/research project that combines
data engineering, wireless-security telemetry, supervised ML, anomaly
detection, model evaluation, explainability, MLOps foundations, risk analysis
and — in later releases — passive Wi‑Fi monitoring, authorized lab experiments,
grounded AI analysis and a SOC-style dashboard.

## v0.4 — Research Dataset & Evaluation Layer

v0.4 moves the project from synthetic-only ML experiments toward a real
wireless intrusion-detection research workflow.

### New in v0.4

- AWID3-style CSV adapter;
- 16-feature IEEE 802.11 research schema;
- automatic label-column detection;
- common AWID3 column aliases;
- binary Normal/Attack target mapping;
- dataset profiling;
- target-leakage checks;
- numeric/categorical preprocessing inside ML pipelines;
- 70/15/15 train-validation-test split;
- Logistic Regression AWID3 pipeline;
- Random Forest AWID3 pipeline;
- validation model selection + separate test reporting;
- held-out permutation feature importance;
- structured research JSON report;
- optional MLflow tracking adapter;
- optional SHAP dependency group;
- `/research/awid3/schema` API endpoint;
- AWID3 research documentation;
- expanded CI and tests.

## Existing ML Core

The earlier aggregated-feature pipeline remains available and contains:

- data validation;
- Logistic Regression;
- Random Forest;
- Histogram Gradient Boosting;
- Isolation Forest;
- benchmark reports;
- experiment storage;
- Incident/Risk Engine;
- FastAPI.

## Install

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m pytest
```

## Demo pipeline

```powershell
python scripts/generate_demo_data.py
python scripts/validate_dataset.py data/demo/wifi_events.csv
python scripts/train_benchmark.py data/demo/wifi_events.csv
```

## AWID3-shaped research smoke test

This fixture has the same selected column structure but is still synthetic:

```powershell
python scripts/generate_awid3_fixture.py
python scripts/inspect_awid3.py data/demo/awid3_fixture.csv
python scripts/train_awid3.py data/demo/awid3_fixture.csv
```

## Real AWID3 workflow

After obtaining an AWID3 CSV according to the dataset owner's terms:

```powershell
python scripts/inspect_awid3.py "C:\path\to\AWID3.csv"
python scripts/train_awid3.py "C:\path\to\AWID3.csv"
```

See `docs/awid3.md`.

## API

```powershell
python -m uvicorn vantawave.api.main:app --reload
```

Then open:

`http://127.0.0.1:8000/docs`

## Research integrity

Synthetic metrics are **not** real-world Wi‑Fi IDS results. Real performance
claims require actual external research data or authorized lab captures.

The project deliberately keeps preprocessing inside trainable pipelines and
maintains a separate test set so that test results are not used as model
selection criteria.
