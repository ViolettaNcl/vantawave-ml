# Final Validation Checklist

## Automated — completed by repository

- [x] Python test suite.
- [x] Python compile check.
- [x] Dashboard route/assets.
- [x] RAG indexing.
- [x] Grounded analyst demo.
- [x] SQLite persistence.
- [x] Alembic migration on SQLite.
- [x] Release file/secret hygiene checks.

## Must be run on the user's Windows machine

- [ ] `python scripts/sensor_capabilities.py`
- [ ] `python scripts/scan_wifi.py --once`
- [ ] dashboard live Windows scan
- [ ] fixed MLflow workflow on the user's exact Windows environment
- [ ] optional PCAP replay with an authorized capture

## Must be run when Docker Desktop is available

- [ ] `docker compose config`
- [ ] `docker compose up --build`
- [ ] PostgreSQL migration
- [ ] `/ready` with required database
- [ ] dashboard through production container

## Required before publishing real model-performance claims

- [ ] Obtain external research dataset under its terms.
- [ ] Run the real research pipeline.
- [ ] Preserve train/validation/test separation.
- [ ] Record error analysis.
- [ ] Record threshold calibration.
- [ ] Store model/report artifacts.
- [ ] Repeat on authorized local telemetry.
- [ ] Compare domain shift between research and local telemetry.

Items above are intentionally not marked complete without evidence from the
actual external dataset/user hardware.
