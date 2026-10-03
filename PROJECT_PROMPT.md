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

v0.11 combines v0.10 and v0.11.

The platform now includes persisted security evidence, local/semantic RAG,
grounded Security Analyst reports with citations, restricted read-only agent
planning, environment configuration, structured logs, readiness checks,
Docker/Compose and PostgreSQL production deployment.

Future work must preserve:

- AI claims are grounded in persisted evidence or retrieved knowledge;
- unsupported evidence produces uncertainty rather than invented facts;
- citations must come from the supplied evidence allow-list;
- AI/agent actions remain read-only and defensive;
- production secrets stay outside source control;
- database schema changes use Alembic;
- readiness is distinct from process liveness.
