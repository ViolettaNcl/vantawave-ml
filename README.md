# VantaWave ML

**End-to-end Wi‑Fi Security, Machine Learning, MLOps, Grounded AI & SOC Platform**

VantaWave ML is a portfolio/research platform that connects wireless telemetry,
classical ML, deep anomaly detection, experiment/model lifecycle, authorized
security-lab evidence, persistent monitoring, grounded RAG analysis and a
production SOC dashboard.

> Current release: **v1.0.2**

## What it demonstrates

- Python engineering and testing
- data validation / leakage controls
- classical ML benchmarking
- anomaly detection
- PyTorch Autoencoder
- threshold calibration
- error analysis
- explainability
- MLflow / model registry
- passive Wi‑Fi telemetry
- offline 802.11 PCAP replay
- authorized lab evidence workflow
- SQLAlchemy / Alembic
- SQLite / PostgreSQL
- drift monitoring
- retraining policy
- grounded RAG / citations
- production FastAPI
- Docker / Compose
- built-in SOC dashboard

## Architecture

```text
Wi-Fi / PCAP / Research Dataset
            ↓
     Sensor + Data Layer
            ↓
  Normalized Feature Windows
            ↓
 Classical ML + Autoencoder
            ↓
 Evaluation / Registry / SHAP
            ↓
       Risk + Incidents
            ↓
 Monitoring + SQL Persistence
            ↓
  Evidence + RAG Retrieval
            ↓
 Grounded Security Analyst
            ↓
   FastAPI + SOC Dashboard
```

See `docs/final_architecture.md`.

## Quick start

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e ".[dev,deep]"

python -m pytest
python scripts/final_portfolio_check.py
```

## Launch the final portfolio demo

Seed local demonstration records:

```powershell
python scripts/seed_portfolio_demo.py
python scripts/build_knowledge_index.py docs
```

Run API:

```powershell
python -m uvicorn vantawave.api.main:app --reload
```

Open:

- **SOC Dashboard:** `http://127.0.0.1:8000/dashboard`
- **API Docs:** `http://127.0.0.1:8000/docs`
- **Readiness:** `http://127.0.0.1:8000/ready`

The seeded incident ID is:

```text
portfolio-incident
```

Use it in the **AI Analyst** section of the dashboard.


## Wi-Fi Recovery

v1.0.1 adds a local Windows recovery assistant.

Open:

```text
http://127.0.0.1:8000/dashboard
```

and select **Wi-Fi Recovery**.

It can:

- scan nearby Wi-Fi networks through Windows;
- list Windows-saved Wi-Fi profiles;
- reveal a key only when Windows already has it saved and local secret viewing
  is explicitly enabled;
- show legitimate router recovery options when no profile exists;
- audit a password supplied locally;
- connect Windows using a WPA2/WPA3 passphrase you supply;
- remove the saved profile afterwards.

If this laptop has never connected to the SSID, there is no stored Windows key
to reveal. VantaWave does not claim to derive an unknown WPA2/WPA3 password
from the air.

See `docs/wifi_recovery.md`.

## Machine Learning layers

### Supervised baselines

- Logistic Regression
- Random Forest
- Histogram Gradient Boosting
- optional CatBoost

### Anomaly detection

- Isolation Forest
- PyTorch Autoencoder trained on normal-only traffic

### Evaluation

- Precision
- Recall
- F1
- PR-AUC
- ROC-AUC
- false-positive / false-negative rate
- confusion matrix
- threshold calibration
- known/unknown anomaly recall
- error analysis

### MLOps

- experiment store
- model versions
- local registry
- candidate/champion lifecycle
- MLflow integration
- SHAP / permutation importance
- promotion guardrails
- feature / anomaly-score drift
- retraining recommendation

## Passive Wi-Fi telemetry

Windows OS-visible scan:

```powershell
python scripts/sensor_capabilities.py
python scripts/scan_wifi.py --once
```

Session:

```powershell
python scripts/scan_wifi.py --duration 30 --interval 5 --window 60
```

Offline 802.11 replay:

```powershell
pip install -e ".[pcap]"
python scripts/inspect_pcap.py "C:\path\to\authorized-capture.pcapng"
```

Windows OS discovery is explicitly distinguished from raw monitor-mode capture.

## Authorized Security Lab

Register only equipment you own or are explicitly allowed to test:

```powershell
python scripts/lab_register_target.py `
  --name "Home Lab AP" `
  --ssid "My-Lab-WiFi" `
  --bssid "00:11:22:33:44:55" `
  --confirm "I own this access point and explicitly authorize security testing."
```

The lab layer supports:

- stable target IDs
- session lifecycle
- before/after telemetry
- evidence SHA-256
- risk/incidents
- experiment reports

## Grounded AI Security Analyst

The AI layer is **not the detector**.

It reads:

- persisted incident fields
- incident evidence
- historical incidents
- retrieved knowledge chunks

and produces evidence-grounded reports with stable citations.

Default retrieval is local TF-IDF. Optional semantic embeddings:

```powershell
pip install -e ".[embeddings]"
```

The restricted agent planner does not permit packet injection, credential
theft, brute force, exploit execution or third-party targeting.

## Persistent data

Default:

```text
SQLite
```

Production option:

```text
PostgreSQL + Psycopg 3
```

Migrations:

```powershell
alembic upgrade head
```

## Docker

```powershell
Copy-Item .env.example .env
docker compose config
docker compose up --build
```

The production stack uses:

- non-root API container
- PostgreSQL
- Alembic migration before startup
- readiness/health checks
- structured JSON logs

## Portfolio documents

- `docs/final_architecture.md`
- `docs/demo_walkthrough.md`
- `INTERVIEW_DEFENSE.md`
- `FINAL_VALIDATION.md`
- `RELEASE_NOTES.md`

## Research integrity

The repository contains synthetic fixtures to make the complete pipeline
reproducible.

**Synthetic results must not be presented as real-world Wi‑Fi IDS performance.**

Before publishing real performance claims, complete the external-dataset and
authorized-hardware items in `FINAL_VALIDATION.md`.

## Security scope

VantaWave is designed for:

- defensive analysis
- your own equipment
- explicitly authorized lab targets
- public research datasets under their terms
- offline captures you are authorized to analyze

It is not presented as a universal Wi‑Fi access/bypass tool.


## Authorized Capture Audit

v1.0.2 adds an Aircrack-ng-inspired **authorized capture verification** workflow.

It does **not** implement `SSID → unknown password`.

Instead:

```text
Authorized Lab target
  → upload PCAP/PCAPNG/CAP
  → detect target + EAPOL evidence
  → verify one locally supplied WPA2 candidate
  → hold verified candidate temporarily in memory
  → Connect verified
```

Dashboard:

```text
http://127.0.0.1:8000/dashboard
```

Select **Capture Audit**.

Requirements:

```powershell
python -m pip install -e ".[dev,deep,pcap]"
```

Aircrack-ng must also be installed locally. VantaWave looks in `PATH`, or you can set:

```powershell
$env:VANTAWAVE_AIRCRACK_PATH="C:\Tools\aircrack-ng\aircrack-ng.exe"
```

The API intentionally exposes no wordlist or brute-force endpoint.

When a candidate is verified, the UI shows a mask such as:

```text
••••••••••••
```

The mask itself is not the password. **Connect verified** uses the actual verified
candidate from an in-memory, short-lived secret vault.

If you explicitly enable local secret viewing:

```powershell
$env:VANTAWAVE_ALLOW_LOCAL_CREDENTIAL_VIEW="true"
```

then **Copy verified secret** can copy the real in-memory candidate on localhost.

See `docs/authorized_capture_audit.md`.
