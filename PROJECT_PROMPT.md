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

VantaWave ML v1.1.0 is the polished portfolio release.

It includes:
- passive Windows Wi-Fi telemetry;
- offline PCAP replay;
- classical/deep ML;
- MLOps/model lifecycle;
- Authorized Lab;
- persistent monitoring;
- grounded AI/RAG;
- SOC Dashboard;
- Wi-Fi Recovery;
- Authorized Capture Audit;
- safe Adversary Simulation;
- Docker/PostgreSQL production engineering.

Adversary Simulation is synthetic-only:
- no packet transmission;
- no external targets;
- no real credential testing;
- no password recovery;
- no active attack execution.

Simulation output uses the same event/feature/risk pipeline for repeatable
red-team/blue-team demonstrations and tests.

Preserve:
- authorization boundaries;
- evidence provenance;
- distinction between synthetic and real telemetry;
- held-out evaluation discipline;
- secret hygiene;
- grounded AI citations;
- no fabricated real-world performance claims.
