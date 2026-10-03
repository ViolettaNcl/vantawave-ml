from vantawave.ml.explainability.shap_explainer import is_shap_available


def test_shap_capability_check_returns_boolean():
    assert isinstance(is_shap_available(), bool)
