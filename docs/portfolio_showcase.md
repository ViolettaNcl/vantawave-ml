# Portfolio Showcase

## Recommended GitHub review path

For a recruiter or senior engineer reviewing VantaWave for the first time:

1. `README.md`
2. `docs/final_architecture.md`
3. `src/vantawave/ml/`
4. `src/vantawave/sensors/`
5. `src/vantawave/monitoring/`
6. `src/vantawave/ai/`
7. `src/vantawave/simulation/`
8. `tests/`
9. `INTERVIEW_DEFENSE.md`

## Engineering signals demonstrated

### ML Engineering

- leakage-aware preprocessing;
- train/validation/test discipline;
- model benchmarking;
- threshold calibration;
- error analysis;
- promotion guardrails;
- anomaly detection;
- deep learning;
- explainability.

### MLOps

- experiment persistence;
- model registry;
- champion/candidate lifecycle;
- MLflow integration;
- drift monitoring;
- retraining recommendations.

### Backend Engineering

- FastAPI;
- structured schemas;
- service boundaries;
- SQLAlchemy;
- Alembic;
- PostgreSQL;
- readiness/liveness.

### Security Engineering

- normalized 802.11 events;
- evidence provenance;
- authorized-target registry;
- capture audit;
- incident/risk pipeline;
- synthetic adversary simulation.

### AI Engineering

- local retrieval;
- optional semantic embeddings;
- grounded evidence contract;
- citation validation;
- restricted read-only agent planning.

### Production Engineering

- Docker;
- Compose;
- non-root runtime;
- CI;
- security scanning;
- structured logs;
- release validation.

## Demo recommendation

Use:

```powershell
python scripts/seed_portfolio_demo.py
python scripts/build_knowledge_index.py docs
python -m uvicorn vantawave.api.main:app --reload
```

Then show:

1. Overview.
2. Adversary Simulation.
3. Monitoring.
4. Incident.
5. AI Analyst.
6. Architecture diagram.

This gives the clearest end-to-end story in a short interview.
