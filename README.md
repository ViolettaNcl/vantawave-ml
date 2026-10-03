# VantaWave ML

**Wi‑Fi Security, Machine Learning, MLOps & AI Research Platform**

VantaWave ML is an independent portfolio/research project that combines
wireless-security data engineering, supervised ML, anomaly detection,
threshold calibration, model evaluation, experiment tracking, model registry,
explainability, risk analysis and — in later versions — passive telemetry,
authorized lab validation, grounded AI analysis and a SOC-style interface.

## v0.5 — MLOps, Calibration, Explainability & Promotion

This release turns the v0.4 research pipeline into a model-lifecycle workflow.

### New in v0.5

- validation-only threshold calibration;
- calibrated held-out test evaluation;
- false-positive / false-negative error analysis;
- transparent promotion policy;
- local model registry with versions, SHA-256 and aliases;
- `candidate` / `champion` model lifecycle;
- optional MLflow tracking and Model Registry;
- optional SHAP TreeExplainer support;
- richer JSON + Markdown research reports;
- local MLflow SQLite configuration;
- expanded MLOps API endpoints;
- expanded automated tests.

## Install — base development

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m pytest
```

## v0.5 smoke run

```powershell
python scripts/generate_awid3_fixture.py
python scripts/run_v05_research.py data/demo/awid3_fixture.csv
```

Generated outputs are written to:

```text
artifacts/v05/
├── models/
├── experiments/
├── registry/
│   ├── registry.json
│   └── models/
├── research_report.json
└── research_report.md
```

## Enable SHAP

```powershell
pip install -e ".[dev,explain]"
python scripts/run_v05_research.py data/demo/awid3_fixture.csv --shap
```

## Enable MLflow

```powershell
pip install -e ".[dev,mlops]"
python scripts/run_v05_research.py data/demo/awid3_fixture.csv --mlflow
python scripts/mlflow_info.py
```

MLflow uses a local SQLite-backed tracking/registry store. This keeps model
lineage, versions, aliases and run metrics inspectable through MLflow.

## Full research extras

```powershell
pip install -e ".[dev,full]"
```

Then:

```powershell
python scripts/run_v05_research.py data/demo/awid3_fixture.csv --shap --mlflow
```

## Real AWID3 workflow

After obtaining an AWID3 CSV under the dataset owner's terms:

```powershell
python scripts/inspect_awid3.py "C:\path\to\AWID3.csv"
python scripts/run_v05_research.py "C:\path\to\AWID3.csv"
```

Add `--shap` and/or `--mlflow` after installing the relevant extras.

## API

```powershell
python -m uvicorn vantawave.api.main:app --reload
```

Useful v0.5 endpoints:

- `/mlops/capabilities`
- `/registry/models`
- `/experiments`
- `/promotion/policy`
- `/research/awid3/schema`
- `/models`
- `/risk/score`
- `/docs`

## Promotion policy

Default candidate requirements:

- test F1 >= 0.80;
- test PR-AUC >= 0.85;
- test FPR <= 0.10;
- validation/test F1 gap <= 0.10.

These are explicit engineering defaults, not universal cybersecurity rules.

## Research integrity

Threshold selection is performed on the validation set. The resulting
threshold is frozen before final test evaluation.

Synthetic fixture metrics only validate the pipeline. They are not real-world
Wi‑Fi IDS performance claims.
