from pathlib import Path

from vantawave.registry.local import LocalModelRegistry


def test_registry_versions_and_promotes(tmp_path):
    source = tmp_path / "model.joblib"
    source.write_bytes(b"model-bytes")

    registry = LocalModelRegistry(tmp_path / "registry")
    first = registry.register(
        model_name="wifi-model",
        artifact_path=source,
        metrics={"f1": 0.8},
        threshold=0.4,
    )
    second = registry.register(
        model_name="wifi-model",
        artifact_path=source,
        metrics={"f1": 0.9},
        threshold=0.5,
    )

    assert first.version == 1
    assert second.version == 2
    assert Path(second.artifact_path).exists()

    promoted = registry.promote_to_champion("wifi-model", 2)
    assert promoted["status"] == "champion"
    assert "champion" in promoted["aliases"]

    models = registry.list_models("wifi-model")
    old = next(item for item in models if item["version"] == 1)
    assert old["status"] == "candidate"
