# VantaWave ML

**Authorized Wi‑Fi Security Research & ML Anomaly Detection Lab**

VantaWave is a learning project for studying wireless-network telemetry,
machine-learning based anomaly detection, attack classification, model
evaluation, and defensive security workflows on networks you own or are
explicitly authorized to test.

## Core goals

- Build a reproducible Wi‑Fi telemetry pipeline.
- Learn feature engineering for 802.11/network events.
- Train a baseline anomaly detector.
- Add supervised attack classification using public research datasets.
- Measure precision, recall, F1, PR-AUC, false-positive rate and latency.
- Add a web/API layer for experiments and incident review.
- Add an allowlisted lab mode so active experiments can only target registered
  laboratory access points.
- Later integrate selected Wi‑Fi sensor functionality inspired by Wifit3.

## Upstream reference

Wifit3:
https://github.com/derv82/wifit3

Keep upstream attribution and license terms if code is copied or adapted.

## Proposed architecture

Wi-Fi sensor / dataset
        |
        v
Telemetry normalizer
        |
        v
Feature extractor
        |
        +--> supervised classifier
        |
        +--> anomaly detector
        |
        v
Risk / incident engine
        |
        v
FastAPI + dashboard + experiment reports

## First milestone

1. Use CSV research data or your own benign telemetry.
2. Produce a fixed feature table.
3. Train Isolation Forest baseline.
4. Save metrics and predictions.
5. Add tests that prevent unregistered lab targets.
6. Only after the ML baseline works, integrate live Wi‑Fi telemetry.

## Safety scope

This repository is designed for:
- your own router/test SSID;
- equipment you control;
- an isolated lab;
- networks where you have explicit permission.

It is not intended to automate access to arbitrary third-party networks.
