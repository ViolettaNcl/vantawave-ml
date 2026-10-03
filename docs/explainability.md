# Explainability

v0.5 keeps model-agnostic permutation importance from v0.4 and adds optional
SHAP support.

Install:

```powershell
pip install -e ".[explain]"
```

Run:

```powershell
python scripts/run_v05_research.py data/demo/awid3_fixture.csv --shap
```

For the current AWID3 Random Forest pipeline, VantaWave transforms the selected
test rows through the fitted preprocessing pipeline and then applies
`shap.TreeExplainer` to the fitted tree estimator.

The report stores mean absolute SHAP contributions for the transformed
features.

SHAP is not used to create the model prediction. It explains the fitted model's
behavior after training.
