# Portfolio Demo Walkthrough

## 1. Verify repository

```powershell
python -m pytest
python scripts/final_portfolio_check.py
```

Expected project test suite: all tests pass.

## 2. Seed dashboard demonstration data

```powershell
python scripts/seed_portfolio_demo.py
```

This creates local, clearly marked demo records.

## 3. Build RAG knowledge manifest

```powershell
python scripts/build_knowledge_index.py docs
```

## 4. Start API

```powershell
python -m uvicorn vantawave.api.main:app --reload
```

Open:

- Dashboard: `http://127.0.0.1:8000/dashboard`
- API: `http://127.0.0.1:8000/docs`
- Readiness: `http://127.0.0.1:8000/ready`

## 5. Dashboard sequence

Show:

1. Overview/readiness.
2. Sensor capabilities.
3. Incident `portfolio-incident`.
4. Model registry/monitoring.
5. Authorized Lab.
6. AI Analyst.

In AI Analyst use:

- Incident ID: `portfolio-incident`
- Question: `What evidence is recorded and what should I verify defensively?`

## 6. Deep anomaly pipeline

```powershell
pip install -e ".[dev,deep]"
python scripts/generate_awid3_fixture.py
python scripts/run_v06_deep.py data/demo/awid3_fixture.csv
```

Explain that fixture results validate the pipeline, not real-world performance.

## 7. Passive Windows sensor

On Windows:

```powershell
python scripts/sensor_capabilities.py
python scripts/scan_wifi.py --once
```

Explain that this is OS-level discovery, not raw monitor mode.

## 8. Production stack

With Docker installed:

```powershell
Copy-Item .env.example .env
docker compose config
docker compose up --build
```

Then open `/ready`.

## 9. Real-world validation

Before claiming real detection performance, run:

- a real external research dataset;
- authorized local telemetry;
- held-out evaluation.

Record the resulting report separately from synthetic demo metrics.


## Adversary Simulation

For the clearest live interview demonstration:

```powershell
python scripts/run_adversary_simulation.py deauth_burst --intensity 4
```

Or use the **Adversary Simulation** page in the SOC dashboard.

Recommended sequence:

1. Start with the normal baseline.
2. Run `Deauthentication burst`.
3. Show the feature deltas.
4. Show anomaly/confidence/risk.
5. Run `Rogue AP presence`.
6. Explain why the unexpected BSSID changes topology features.
7. Open the generated Markdown simulation report.
8. Emphasize that the scenario is synthetic and transmits no packets.

This gives a repeatable security demo without depending on radio hardware or
performing active attacks.
