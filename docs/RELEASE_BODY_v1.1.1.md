# VantaWave ML v1.1.1 — Launch Ready

VantaWave ML is an end-to-end defensive Wi-Fi security and ML platform that connects telemetry, anomaly detection, MLOps, monitoring, authorized lab evidence, grounded AI analysis, and a SOC dashboard.

## Highlights

- Classical ML + PyTorch Autoencoder + Isolation Forest
- Threshold calibration, error analysis, promotion guardrails
- MLflow, SHAP, experiment/model registry
- Passive Windows WLAN telemetry and offline PCAP replay
- Authorized Lab + evidence bundles
- Persistent monitoring and drift detection
- Grounded RAG Security Analyst with citations
- Safe synthetic Adversary Simulation
- FastAPI SOC Dashboard
- Docker + PostgreSQL production stack
- Read-only GitHub Pages demo

## Launch-ready improvements

- Apache-2.0 license
- reproducible Ruff 0.16.10 configuration
- CI lint policy focused on correctness rules
- social preview asset
- dashboard demo animation
- live static demo under `docs/`
- citation metadata
- launch/community documentation

## Validation

```text
115 automated tests
release validation
simulation API E2E
wheel build
secret hygiene checks
```

Synthetic demo results are explicitly separated from real-world benchmark claims.

## Try it

```powershell
git clone https://github.com/ViolettaNcl/vantawave-ml.git
cd vantawave-ml
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,deep,pcap]"
python -m pytest
python -m uvicorn vantawave.api.main:app --reload
```

Dashboard: `http://127.0.0.1:8000/dashboard`

Live read-only demo after Pages is enabled: `https://violettancl.github.io/vantawave-ml/`
