# VantaWave ML

**Wi‑Fi Security, Passive Telemetry, Authorized Lab, Machine Learning, MLOps, Grounded AI/RAG & Production Engineering Platform**

VantaWave ML is an end-to-end portfolio/research platform that connects
wireless telemetry, ML/deep anomaly detection, experiment/model lifecycle,
authorized lab evidence, persistent monitoring, grounded AI analysis and
production deployment.

## v0.11 — Combined AI + Production Release

This release contains both planned stages:

- **v0.10 — AI Security Analyst + RAG**
- **v0.11 — Production Engineering**

There is no need to commit a separate v0.10. v0.11 contains it.

### AI / RAG

- local knowledge-base ingestion;
- deterministic document chunking;
- TF-IDF retrieval;
- optional Sentence Transformers semantic retrieval;
- persisted-incident analysis;
- historical incident similarity;
- explicit evidence references;
- citation allow-list validation;
- grounded prompt contract for LLM integration;
- restricted read-only agent planner;
- defensive action suggestions;
- no autonomous attack execution.

### Production Engineering

- environment-based configuration;
- structured JSON logging;
- `/ready` readiness checks;
- `/config/public`;
- Docker multi-stage build;
- non-root runtime container;
- Docker Compose API + PostgreSQL;
- Alembic migration on container startup;
- container healthcheck;
- `.env.example`;
- security CI with dependency audit, Bandit and Docker build;
- production launcher.

## Current architecture

```text
Passive Wi-Fi Sensor / PCAP / Research Dataset
                    ↓
            Normalized Telemetry
                    ↓
         Rolling Feature Windows
                    ↓
      Classical ML + Deep Anomaly
                    ↓
           Risk / Incidents
                    ↓
     Drift + Persistent Monitoring
                    ↓
      SQLAlchemy / PostgreSQL
                    ↓
          Evidence + History
                    ↓
            RAG Retrieval
                    ↓
      Grounded Security Analyst
                    ↓
       API / Production Runtime
```

## Local development

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e ".[dev,deep]"

python -m pytest
```

## Knowledge-base smoke test

```powershell
python scripts/build_knowledge_index.py docs
```

## AI Analyst demo

```powershell
python scripts/ai_analyst_demo.py
```

The demo creates persisted incident evidence and generates a grounded report
using project documentation and incident history.

## Start API

```powershell
python -m uvicorn vantawave.api.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Notable endpoints:

- `GET /health`
- `GET /ready`
- `GET /config/public`
- `GET /ai/capabilities`
- `GET /ai/analyze/{incident_id}`
- `GET /sensors/capabilities`
- `GET /lab/capabilities`
- `GET /monitoring/recent`
- `GET /registry/models`
- `GET /experiments`

## Optional semantic embeddings

```powershell
pip install -e ".[embeddings]"
```

The default TF-IDF retriever remains available without downloading an embedding
model.

## Production stack

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Build/run:

```powershell
docker compose up --build
```

The stack starts:

- PostgreSQL;
- VantaWave API;
- Alembic migrations.

## Readiness

`/health` means the API process is running.

`/ready` checks runtime dependencies and, in production Compose, requires the
database to be reachable.

## Security Analyst boundaries

The AI layer may:

- summarize persisted incidents;
- retrieve project knowledge;
- compare historical incidents;
- suggest defensive checks;
- generate evidence-grounded reports.

It does not autonomously perform:

- packet injection;
- brute force;
- credential theft;
- exploit execution;
- third-party targeting.

## Important research limitation

The repository still requires a final benchmark on a real external wireless
research dataset and an authorized local telemetry demonstration before
real-world model-performance claims should be made.
