# Drift Monitoring Foundation

v0.6 introduces a baseline representation of normal training traffic.

## Numeric features

Stored:

- mean;
- standard deviation.

Current comparison score:

`abs(current_mean - reference_mean) / reference_std`

This is a simple standardized mean-shift indicator.

## Categorical features

Stored:

- empirical category frequency distribution.

Current comparison score:

- total variation distance.

## Important limitation

These are baseline monitoring signals, not a mature drift-detection system.

Later releases will add:

- windowed history;
- PSI/KS-style tests where appropriate;
- alert thresholds based on real telemetry;
- anomaly-score drift;
- model performance drift;
- retraining recommendations.
