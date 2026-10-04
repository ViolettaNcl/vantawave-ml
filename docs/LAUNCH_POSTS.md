# Launch Post Drafts

Use these as starting points. Adapt them to each community instead of cross-posting identical text everywhere.

## LinkedIn

I wanted to build an ML project that went beyond a notebook and an accuracy score, so I built **VantaWave ML**.

It is an end-to-end Wi-Fi security research platform that connects:

- passive telemetry and PCAP analysis
- classical ML + PyTorch anomaly detection
- threshold calibration and error analysis
- MLflow / model registry / SHAP
- drift monitoring and retraining recommendations
- authorized security-lab evidence
- grounded RAG incident analysis
- a FastAPI SOC dashboard
- Docker/PostgreSQL production engineering

I also added a safe adversary-simulation layer so the detection pipeline can be demonstrated without attacking a real network.

The part I care most about is research honesty: synthetic fixture metrics are clearly separated from real-world benchmark claims.

GitHub: https://github.com/ViolettaNcl/vantawave-ml

Feedback on the architecture, ML evaluation, and security-monitoring design is welcome.

## Hacker News — Show HN

**Title:** Show HN: VantaWave – an ML-powered Wi-Fi security research and SOC platform

**Body:**

I built VantaWave ML as an attempt to make a security/ML portfolio project that does not stop at model training.

The pipeline covers Wi-Fi telemetry/PCAP normalization, classical models, Isolation Forest, a PyTorch Autoencoder, threshold calibration, model promotion, MLflow/SHAP, persistent drift monitoring, incident/risk handling, a grounded RAG analyst, and a built-in SOC dashboard.

There is also a synthetic adversary-simulation layer for repeatable deauth/rogue-AP/auth/retry scenarios without transmitting packets.

One deliberate choice: synthetic demo metrics are not presented as real-world IDS accuracy. A real external benchmark remains a separate validation step.

Repo: https://github.com/ViolettaNcl/vantawave-ml

I would especially appreciate criticism of the ML evaluation design and the boundary between detection evidence and LLM explanation.

## Reddit / ML-security community

**Title:** I built an end-to-end Wi-Fi anomaly-detection platform instead of another notebook-only ML project

I have been building VantaWave ML, a Python project that combines wireless telemetry with classical ML, deep anomaly detection, MLOps, drift monitoring, and a small SOC interface.

The current architecture includes Logistic Regression / Random Forest / HGB, Isolation Forest, a normal-only PyTorch Autoencoder, validation-only threshold calibration, error analysis, model promotion, MLflow/SHAP, and a grounded RAG analyst that is not allowed to invent detector evidence.

For repeatable testing I added synthetic adversary scenarios, but the README explicitly separates those from real benchmark claims.

I am looking for technical feedback rather than just stars—especially on evaluation methodology, false-positive control, and useful public wireless-security datasets.

https://github.com/ViolettaNcl/vantawave-ml

## DEV.to / Medium article outline

**Title:** From Wi-Fi Telemetry to a Production ML Security Platform: Building VantaWave ML

1. Why notebook-only ML was not enough
2. Normalizing wireless telemetry
3. Leakage-safe model evaluation
4. Supervised baselines vs anomaly detection
5. Why the Autoencoder trains on normal-only traffic
6. Threshold calibration and false positives
7. Model registry, explainability and drift
8. Evidence-first incident handling
9. Why the LLM is not the detector
10. Safe adversary simulation
11. Docker/PostgreSQL/SOC dashboard
12. What remains before real-world performance claims

End with the architecture diagram and repository link.
