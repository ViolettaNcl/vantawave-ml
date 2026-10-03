# Threshold Calibration

Binary classifiers often default to threshold `0.5`, but that is not
automatically the best operating point for intrusion detection.

VantaWave v0.5 calibrates the threshold using **validation data only**.

The default policy searches thresholds from 0.05 to 0.95 and maximizes F1
subject to:

- validation precision >= 0.60;
- validation false-positive rate <= 0.20.

The chosen threshold is then frozen and evaluated on the held-out test set.

This avoids choosing a threshold after seeing test performance.

The report records:

- chosen threshold;
- validation precision/recall/F1/FPR;
- calibrated test precision/recall/F1/FPR;
- default probability metrics such as PR-AUC.
