# Persistent Data Layer

## Stack

VantaWave v0.9 uses SQLAlchemy 2.x.

Local default:

- SQLite.

Production-ready option:

- PostgreSQL via Psycopg 3.

Database URL is controlled by:

`VANTAWAVE_DATABASE_URL`

## Tables

### `lab_targets`
Authorized AP metadata and authorization confirmation.

### `sensor_sessions`
Persistent collection/lab-session metadata.

### `incidents`
Risk/anomaly incidents and evidence metadata.

### `drift_events`
Feature/anomaly-score drift findings.

### `model_snapshots`
Model version/alias/threshold/metric snapshots.

### `evaluation_runs`
Periodic evaluation results and retraining decisions.

## Migrations

Alembic manages schema migrations.

```powershell
alembic upgrade head
```

The first migration is `0001_initial`.

## SQLite vs PostgreSQL

SQLite is the default because it requires no server and makes the repository
easy to run for reviewers.

PostgreSQL is supported by changing only the database URL. The application
repository/service layer does not require a separate implementation.
