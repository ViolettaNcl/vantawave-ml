# MLOps in VantaWave ML v0.5

v0.5 introduces two complementary model-lifecycle layers.

## 1. Local registry

The built-in `LocalModelRegistry` works without external services.

It stores:

- model name;
- monotonically increasing version;
- model ID;
- copied model artifact;
- SHA-256 digest;
- metrics;
- calibrated threshold;
- status;
- aliases;
- metadata;
- creation time.

A model that passes promotion policy can be assigned the `champion` alias.
The previous champion is archived.

This makes the model-promotion logic testable even when MLflow is not installed.

## 2. MLflow integration

Install:

```powershell
pip install -e ".[mlops]"
```

Run a tracked experiment:

```powershell
python scripts/run_v05_research.py data/demo/awid3_fixture.csv --mlflow
```

Inspect local MLflow configuration:

```powershell
python scripts/mlflow_info.py
```

The project configures a local SQLite-backed MLflow tracking/registry store.
A database-backed store is intentional because MLflow Model Registry requires
one for registry API/UI workflows.

The selected model can be registered in MLflow and assigned a `candidate`
alias. Later production workflow can move an approved version to a
`champion`/production alias.

## Why both?

The local registry is lightweight and deterministic for project tests.

MLflow provides the richer UI, run lineage, model registry, versioning,
aliases, tags, artifacts and future deployment integrations.
