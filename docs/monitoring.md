# Monitoring & Retraining Policy

## Feature drift

The existing drift baseline compares:

- numeric mean shifts;
- categorical total-variation distance.

## Anomaly-score drift

v0.9 stores a score baseline:

- mean;
- standard deviation;
- p50;
- p90;
- p95;
- p99.

A current score window is compared to the reference using standardized mean
shift and the rate of scores exceeding the reference p95.

## Retraining policy

Default policy:

- evaluate every 24 hours;
- retrain if at least 1 high drift finding exists;
- retrain if at least 3 warning drift findings exist;
- retrain if F1 < 0.80;
- retrain if FPR > 0.10.

Every recommendation stores reasons.

These values are transparent project defaults, not universal security
standards.

## Persistence

`persist_monitoring_result()` writes:

- each drift finding;
- model/dataset evaluation;
- recommendation;
- reasons.

This gives later AI/dashboard layers historical context.
