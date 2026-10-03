# Development prompt — VantaWave ML

You are working on `VantaWave-ML`, an authorized Wi‑Fi security and
machine-learning research platform.

## Product goal

Turn the starter repository into a polished portfolio project that demonstrates:

- Python engineering;
- Wi‑Fi/network telemetry understanding;
- data cleaning and feature engineering;
- classical ML;
- anomaly detection;
- experiment tracking;
- model evaluation;
- FastAPI;
- tests;
- Docker;
- clear security boundaries;
- later, defensive AI explanations.

## Non-negotiable scope

Active wireless experiments must only operate on a laboratory AP explicitly
registered by the owner in local configuration. Never add a generic
"hack any Wi-Fi" mode, automatic third-party targeting, credential theft,
or silent expansion to nearby networks.

The project may study attack traces from public research datasets and may
support controlled experiments on the owner's own lab equipment.

## Phase 1 — Repository foundation

- Clean Python package structure.
- Ruff/formatting/type checking.
- Pytest.
- Config loader.
- Structured logging.
- Experiment output directory.
- Reproducible seed handling.

## Phase 2 — Data pipeline

Create adapters for:
1. public Wi‑Fi intrusion datasets;
2. CSV/Parquet experiment captures;
3. later, live telemetry.

Normalize observations into a documented schema.

Candidate features:
- frame/event counts per time window;
- authentication/association rate;
- deauthentication/disassociation rate;
- beacon rate;
- unique clients;
- unique BSSIDs;
- RSSI statistics;
- channel changes;
- retry/error ratios;
- inter-arrival statistics;
- protocol/security-mode metadata.

Prevent target leakage.

## Phase 3 — ML baseline

Implement:
- train/validation/test split appropriate to the dataset;
- StandardScaler where needed;
- Isolation Forest baseline;
- Logistic Regression baseline for labeled data;
- Random Forest / CatBoost or LightGBM comparison;
- confusion matrix;
- precision;
- recall;
- F1;
- PR-AUC;
- false-positive rate.

Do not claim a model is superior without measured results.

## Phase 4 — Unknown-anomaly model

Add:
- Isolation Forest;
- optional One-Class SVM;
- optional Autoencoder in PyTorch.

Train predominantly on normal traffic and evaluate on held-out abnormal
sessions. Report threshold sensitivity.

## Phase 5 — Authorized Lab Mode

Create a target registry:

- friendly name;
- SSID;
- BSSID;
- ownership/authorization flag;
- optional notes;
- test-session ID.

Active experiment code must refuse to proceed when a target is not registered.

Create clear UI states:
`PASSIVE OBSERVATION`, `AUTHORIZED LAB`, `DATASET REPLAY`.

## Phase 6 — Wi‑Fi sensor integration

Study Wifit3 as an upstream reference:
https://github.com/derv82/wifit3

Prefer a clean adapter layer rather than copying large sections blindly.
Preserve attribution and licensing for any adapted upstream code.

The sensor should expose normalized events to the ML pipeline rather than
coupling ML directly to hardware-specific code.

## Phase 7 — API and dashboard

FastAPI endpoints:
- `/health`
- `/models`
- `/experiments`
- `/incidents`
- `/targets`
- `/predict/anomaly`

Dashboard:
- lab target;
- current security mode;
- event timeline;
- anomaly score;
- model confidence;
- model version;
- top contributing features;
- experiment comparison.

## Phase 8 — MLOps

Add:
- MLflow experiment tracking;
- model versioning;
- Docker;
- deterministic training configuration;
- dataset metadata;
- drift report;
- reproducible evaluation report.

## Phase 9 — AI security analyst

Only after the ML system works.

The LLM receives structured incident evidence and produces a human-readable
explanation. It must not fabricate packets, credentials, model scores or
network facts.

## Portfolio quality requirements

README must contain:
- problem statement;
- architecture;
- dataset;
- model comparison;
- metrics;
- limitations;
- screenshots;
- reproducible setup;
- demo scenario;
- ethical/authorization scope.

The final repository should make it clear what was built by this project
versus what comes from upstream libraries or datasets.

## Working style

For every feature:
1. explain the concept briefly;
2. implement the smallest correct version;
3. add tests;
4. run the tests;
5. show measured output;
6. document limitations;
7. only then move to the next feature.

Avoid adding technologies only for appearance.
