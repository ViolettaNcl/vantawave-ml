# MLflow `numpy.dtype` skops Hotfix

On Windows with MLflow 3.x, VantaWave v0.5 encountered:

`UntrustedTypesFoundException: ['numpy.dtype']`

MLflow's scikit-learn flavor supports `skops_trusted_types` for model types
that require explicit trust during safe skops serialization.

v0.6 keeps `serialization_format="skops"` and supplies:

`skops_trusted_types=["numpy.dtype"]`

This is intentionally narrower than switching the entire registry workflow to
pickle/cloudpickle.

Re-test with:

```powershell
pip install -e ".[dev,mlops]"
python scripts/generate_awid3_fixture.py
python scripts/run_v05_research.py data/demo/awid3_fixture.csv --mlflow
```
