from types import SimpleNamespace

from vantawave.mlops.mlflow_backend import sklearn_log_options


def test_mlflow_skops_trusts_numpy_dtype():
    fake = SimpleNamespace(
        sklearn=SimpleNamespace(SERIALIZATION_FORMAT_SKOPS="skops")
    )
    options = sklearn_log_options(fake)
    assert options["serialization_format"] == "skops"
    assert "numpy.dtype" in options["skops_trusted_types"]
