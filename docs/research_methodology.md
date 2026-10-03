# Research Methodology

VantaWave ML separates three concepts:

1. **Demo validation** — synthetic data proves that software paths work.
2. **Research evaluation** — external datasets measure model behavior.
3. **Authorized lab validation** — later versions test generalization on
   locally collected, permitted telemetry.

## Leakage controls

The research layer checks target-like feature names and keeps labels outside
the feature matrix. Preprocessing lives inside fitted pipelines so train-set
statistics are not calculated using validation/test rows.

Further dataset-specific leakage analysis is still required because semantic
leakage cannot always be detected from a column name alone.

## Selection versus final evaluation

Validation F1 is used to identify the strongest baseline. The test split is
reported separately and is not used for selecting the model.

## Explainability

v0.4 uses model-agnostic permutation importance on held-out test data.
SHAP is intentionally optional and will be integrated after the real-data
workflow has been validated.

## Reproducibility

Default random seed: 42.

Generated model artifacts and research reports are stored under `artifacts/`
and are ignored by Git.
