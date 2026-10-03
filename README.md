# VantaWave ML

**Wi‑Fi Security, Passive Telemetry, Authorized Lab, Monitoring, Persistent Data, ML, MLOps & AI Research Platform**

## v0.9 — Monitoring & Data Platform

v0.9 turns VantaWave into a persistent system instead of a collection of
ephemeral experiment files.

### New in v0.9

- SQLAlchemy 2.x ORM data layer;
- SQLite default database for zero-config local development;
- PostgreSQL-ready configuration through `VANTAWAVE_DATABASE_URL`;
- Psycopg 3 optional PostgreSQL driver;
- Alembic migrations;
- persistent lab targets;
- persistent sensor/lab sessions;
- persistent incidents;
- persistent drift events;
- persistent model snapshots;
- persistent evaluation runs;
- anomaly-score drift monitoring;
- feature drift monitoring;
- scheduled evaluation policy;
- retraining recommendations;
- file-state → database import utility;
- database and monitoring API endpoints.

## Install database support

```powershell
pip install -e ".[dev]"
```

For PostgreSQL:

```powershell
pip install -e ".[dev,postgres]"
```

## Initialize local SQLite database

```powershell
python scripts/init_database.py
```

Default file:

```text
artifacts/v09/vantawave.db
```

## Run database demo

```powershell
python scripts/db_demo.py
```

## Run monitoring demo

```powershell
python scripts/monitor_demo.py
```

The monitoring demo evaluates:

- numeric feature drift;
- categorical distribution drift;
- anomaly-score drift;
- current F1/FPR;
- retraining policy.

It then persists drift events and an evaluation run.

## Switch to PostgreSQL

Set:

```powershell
$env:VANTAWAVE_DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/vantawave"
```

Then run:

```powershell
alembic upgrade head
```

VantaWave uses the same SQLAlchemy models for SQLite and PostgreSQL.

## Migrations

Initialize/update schema:

```powershell
alembic upgrade head
```

See current revision:

```powershell
alembic current
```

## Import v0.8 file state

If you already created file-backed lab targets/sessions:

```powershell
python scripts/import_file_state_to_db.py
```

## API

```powershell
python -m uvicorn vantawave.api.main:app --reload
```

New endpoints include:

- `GET /data/capabilities`
- `GET /db/health`
- `GET /monitoring/policy`
- `GET /monitoring/recent`

All previous sensor, lab, ML, registry and experiment endpoints remain.

## Monitoring policy

Current default triggers include:

- high feature/anomaly-score drift;
- repeated warning-level drift;
- F1 below minimum;
- false-positive rate above maximum.

The output is an explicit recommendation:

- `keep_current_model`
- `retrain`

with auditable reasons.

## Architecture after v0.9

```text
Passive Sensor / Dataset
        ↓
Normalized Telemetry
        ↓
Feature Windows
        ↓
ML / Deep Anomaly Detection
        ↓
Incidents + Risk
        ↓
Monitoring / Drift
        ↓
Persistent SQL Data Layer
        ↓
Model Evaluation / Retraining Recommendation
```

## Research integrity

Drift signals are monitoring indicators, not proof of an attack.
Retraining recommendations are rule-based decisions with recorded reasons.
