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

v0.7 adds the passive telemetry architecture:

- normalized `WirelessEvent` schema;
- Windows OS-visible WLAN discovery;
- offline PCAP replay;
- JSONL sensor sessions;
- rolling feature windows;
- network inventory/change detection;
- explicit collection provenance.

Future releases must preserve these rules:

- sensor adapters stay separate from ML models;
- every event records source/collection provenance;
- OS WLAN discovery must not be mislabeled as raw monitor-mode capture;
- live telemetry must not be fed into unrelated synthetic models and presented
  as validated predictions;
- packet injection and active attack automation remain outside the passive
  sensor layer;
- raw live 802.11 capture, when added, belongs only to the authorized-lab
  workflow and must require explicitly registered equipment.
