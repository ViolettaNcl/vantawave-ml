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

VantaWave ML v1.0 is the portfolio release.

The repository now contains the complete architecture from passive telemetry
and ML through monitoring, persistence, grounded RAG, production engineering
and the SOC dashboard.

Do not invent the remaining external evidence.

Before claiming real-world model performance, complete `FINAL_VALIDATION.md`
on the user's actual Windows/hardware environment and a real external research
dataset.

Preserve:
- train/validation/test integrity;
- authorized-target boundaries;
- sensor provenance;
- evidence-grounded AI citations;
- explicit model promotion/retraining rules;
- migration-based database schema changes;
- secret hygiene;
- distinction between synthetic demonstration results and real validation.
