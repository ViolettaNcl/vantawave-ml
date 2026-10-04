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

VantaWave ML v1.0.2 includes the final portfolio platform, Windows Wi-Fi
Recovery and Authorized Capture Audit.

Capture Audit follows an evidence-based WPA/WPA2 workflow:
- explicitly authorized Lab target;
- local PCAP/PCAPNG/CAP analysis;
- target SSID/BSSID matching;
- EAPOL evidence inspection;
- optional Aircrack-ng integration;
- exactly one candidate passphrase per verification request;
- short-lived in-memory verified secret;
- masked UI display;
- connect-with-verified-secret;
- optional localhost-only secret reveal/copy.

It must never claim that an unknown WPA2/WPA3 password can be derived from an
SSID alone. It must not expose a wordlist/brute-force API.

Preserve all previous authorization, secret-handling, research-integrity,
evidence-grounding, database migration and MLOps rules.
