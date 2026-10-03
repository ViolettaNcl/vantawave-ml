# VantaWave ML — Development Prompt

Develop VantaWave ML as an independent Wi-Fi security and machine-learning
research platform.

Priorities:

1. Build a reproducible data pipeline.
2. Use real public research data before claiming real-world performance.
3. Compare simple ML baselines before deep learning.
4. Track experiments and metrics.
5. Add passive live telemetry only after the offline ML pipeline is reliable.
6. Restrict active lab functionality to explicitly registered equipment.
7. Keep the README focused on VantaWave ML's own architecture, experiments,
   results, and limitations.
8. Preserve third-party license and attribution requirements only when actual
   third-party code, models, or datasets are incorporated.
9. Never present synthetic-demo metrics as real-world Wi-Fi security results.
10. Every feature must include tests and a reproducible way to run it.

For each development step:
- explain the concept;
- implement the smallest correct version;
- add tests;
- run them;
- measure the output;
- document limitations;
- then continue.


## Current baseline

v0.5 includes the AWID3 research pipeline, threshold calibration, error
analysis, local model registry, explicit promotion policy, optional MLflow
Model Registry integration, optional SHAP explainability and rich reports.

Future releases must preserve the following rules:

- no threshold selection on the test set;
- no silent promotion of the newest model;
- promotion criteria must remain explicit and auditable;
- model versions must retain lineage/metrics;
- SHAP explains model behavior but does not replace evaluation;
- synthetic fixture results must never be presented as real-world IDS results.
