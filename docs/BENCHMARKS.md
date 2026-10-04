# Benchmarks

## Status

VantaWave has a complete reproducible evaluation pipeline, but this repository does **not** claim real-world Wi-Fi intrusion-detection accuracy from synthetic fixtures.

That distinction is intentional.

## Synthetic pipeline checks

Synthetic fixtures are used to verify:

- preprocessing;
- train/validation/test plumbing;
- threshold calibration;
- registry/report generation;
- Autoencoder/Isolation Forest execution;
- known/unknown anomaly grouping;
- CI reproducibility.

They are not a real-world benchmark.

## External benchmark target

The next publishable benchmark should report at least:

| Model | Precision | Recall | F1 | PR-AUC | ROC-AUC | FPR | FNR |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logistic Regression | — | — | — | — | — | — | — |
| Random Forest | — | — | — | — | — | — | — |
| Isolation Forest | — | — | — | — | — | — | — |
| Autoencoder | — | — | — | — | — | — | — |

The table remains blank until a real external dataset is run end-to-end.

## Reproducibility requirements

Any published benchmark must include:

1. dataset name/version/source;
2. exact feature schema;
3. class mapping;
4. split policy and random seed;
5. leakage audit;
6. validation-only threshold selection;
7. held-out test metrics;
8. confusion matrix and error analysis;
9. dependency/version information;
10. generated machine-readable report artifact.

## Why this matters

A strong GitHub project should make it easy to distinguish:

```text
pipeline works
```

from:

```text
model generalizes in the real world
```

VantaWave treats those as separate claims.
