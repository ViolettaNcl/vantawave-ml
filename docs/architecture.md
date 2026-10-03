# Architecture

Current pipeline:

Dataset
→ loader
→ validation
→ feature matrix
→ split
→ models
→ evaluation
→ artifacts/reports
→ incident/risk layer
→ FastAPI

Future live pipeline:

Wi‑Fi sensor
→ normalized events
→ window aggregation
→ feature matrix
→ classifier + anomaly detector
→ incident engine
→ explainability
→ AI analyst
→ dashboard
