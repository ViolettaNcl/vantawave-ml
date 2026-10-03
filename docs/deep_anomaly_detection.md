# Deep Anomaly Detection

## Goal

The v0.6 Autoencoder is designed to detect behavior that differs from normal
network traffic without requiring every possible attack category during
training.

## Training discipline

Only normal rows are used for:

- fitting the AWID3 preprocessing layer;
- Autoencoder training;
- early-stopping validation;
- reconstruction-error threshold calibration.

Anomaly examples are reserved for final evaluation.

## Threshold

The default threshold is:

`99th percentile(normal validation reconstruction error)`

This is deliberately different from supervised threshold tuning. It prevents
attack labels from being required for the Autoencoder operating point.

## Known and unknown groups

Attack labels are grouped only during evaluation.

Default:

- known: Deauth;
- unknown: RogueAP, Flood.

The Autoencoder does not receive these labels during training.

## Baseline

Isolation Forest is trained on the same normal-only transformed feature space
and calibrated using the same normal-validation quantile principle.

This provides a meaningful classical-vs-deep anomaly comparison.
