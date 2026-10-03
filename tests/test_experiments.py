from vantawave.experiments.store import ExperimentRun, FileExperimentStore

def test_experiment_store_roundtrip(tmp_path):
    store = FileExperimentStore(tmp_path)
    run = ExperimentRun(
        name="demo",
        version="0.3.0",
        params={"seed": 42},
        metrics={"f1": 0.9},
    )
    assert store.save(run).exists()
    runs = store.list_runs()
    assert len(runs) == 1
    assert runs[0]["name"] == "demo"
