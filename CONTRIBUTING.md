# Contributing to VantaWave ML

VantaWave is a defensive security / ML research project. Contributions should
preserve reproducibility, authorization boundaries and evidence integrity.

## Development setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,deep,pcap]"
python -m pytest
```

## Before opening a pull request

Run:

```powershell
python -m pytest
python -m compileall -q src scripts alembic
python scripts/final_portfolio_check.py
```

## Engineering expectations

Prefer:

- small focused modules;
- deterministic tests;
- typed/domain-oriented schemas;
- explicit configuration;
- reproducible evaluation;
- documented safety boundaries.

Avoid:

- hidden side effects;
- hard-coded secrets;
- fabricated benchmark claims;
- feature leakage;
- training/evaluating on the same holdout;
- mixing synthetic evidence with real telemetry without provenance.

## Security contributions

Allowed project directions include:

- passive telemetry;
- authorized offline capture analysis;
- synthetic adversary simulation;
- defensive detection;
- model monitoring;
- evidence-grounded AI;
- secure production engineering.

Do not submit features that turn the project into an arbitrary-network
credential theft, brute-force or active exploitation tool.

## Database changes

Schema changes should use Alembic migrations.

## New ML models

A new model should include:

1. clear feature contract;
2. leakage review;
3. train/validation/test discipline;
4. comparable metrics;
5. error analysis;
6. inference-latency measurement when relevant;
7. tests;
8. documentation.

## New simulation scenarios

Every scenario must explicitly define:

```text
simulated_only = true
transmits_packets = false
```

and document:

- learning goal;
- expected defensive signals;
- safety boundary.

## Documentation

Update the relevant files when behavior changes:

- `README.md`
- `README_RU.md` where useful
- `ROADMAP.md`
- `RELEASE_NOTES.md`
- `FINAL_VALIDATION.md`
- relevant file under `docs/`


## License

By contributing, you agree that your contribution may be distributed under the repository Apache-2.0 license.
