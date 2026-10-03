# VantaWave ML — Interview Defense Guide

## One-minute explanation

VantaWave ML is an end-to-end wireless-security ML platform. I built the
pipeline from data validation and model evaluation through anomaly detection,
MLOps, passive telemetry, persistent monitoring, authorized lab evidence, a
grounded RAG analyst and a production SOC dashboard.

The key design choice is separation of concerns: sensor adapters only collect
and normalize telemetry; models consume features; evaluation controls model
promotion; incidents and evidence are persisted; the AI analyst can only
explain persisted evidence and retrieved documentation.

## Why not just use an LLM?

Because the LLM is not the detector.

Detection comes from measurable ML/anomaly models. The AI layer only explains
existing evidence. This prevents a language model from inventing network facts
or becoming the source of truth.

## Why both classical ML and Autoencoder?

Classical supervised models are strong baselines for known labeled patterns.

The Autoencoder is trained only on normal traffic and can be evaluated against
previously unseen anomaly categories. I compare it against Isolation Forest so
the deep model must justify its added complexity.

## How did you avoid data leakage?

- labels are separated from features;
- preprocessing is fitted inside training pipelines;
- threshold calibration uses validation data;
- final test data is held out;
- feature names are audited for target-like fields;
- real/live telemetry is not presented as valid model input until
  domain-matched evaluation exists.

## What is model promotion?

A new model is not automatically called better.

VantaWave uses explicit promotion guardrails such as F1, PR-AUC, false-positive
rate and validation/test gap. The decision and reasons are stored.

## How is MLOps represented?

- experiment history;
- local registry;
- versioned artifacts;
- model aliases;
- MLflow integration;
- threshold metadata;
- metrics;
- SHAP/permutation explainability;
- drift monitoring;
- retraining recommendations.

## What happens after deployment?

The monitoring layer compares new feature/anomaly-score distributions with a
reference baseline. It persists drift events and can recommend retraining when
explicit guardrails are crossed.

## How is Wi-Fi data collected?

v1.0 supports:

- Windows OS-visible WLAN discovery;
- normalized sensor-event sessions;
- offline 802.11 PCAP replay.

Raw monitor-mode capture is hardware/driver specific and is intentionally
separated into the authorized-lab boundary.

## What does the database contain?

- authorized targets;
- sensor/lab sessions;
- incidents;
- drift events;
- model snapshots;
- evaluation runs.

Local development uses SQLite. PostgreSQL is supported with the same ORM and
Alembic migrations.

## How does the RAG analyst avoid hallucination?

It receives:

1. persisted incident evidence;
2. retrieved project knowledge;
3. historical incident records.

Sources receive stable citations. The prompt exposes only an allow-list of
valid citations, and the citation guard rejects references not present in that
evidence set.

## What would you improve next?

1. Benchmark on the complete real external dataset.
2. Collect authorized local telemetry over multiple days.
3. Calibrate thresholds on domain-matched data.
4. Add real production observability.
5. Add browser-based charts once enough monitoring history exists.
6. Expand the retrieval corpus with curated defensive Wi-Fi documentation.

## What should you never claim?

Do not say:

- the synthetic fixture proves real-world accuracy;
- the Windows OS scan is raw monitor mode;
- a high anomaly score proves compromise;
- the AI analyst discovered facts not present in evidence;
- VantaWave can compromise arbitrary Wi-Fi networks.
