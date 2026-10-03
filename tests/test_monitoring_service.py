import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from vantawave.db.base import Base
from vantawave.db.repositories import DriftRepository, EvaluationRepository
from vantawave.db.session import create_session_factory, session_scope
from vantawave.monitoring.service import evaluate_monitoring_window, persist_monitoring_result


def test_monitoring_result_persists():
    rng = np.random.default_rng(42)
    reference = pd.DataFrame({
        "x": rng.normal(0, 1, 100),
        "kind": rng.choice(["a", "b"], 100),
    })
    current = pd.DataFrame({
        "x": rng.normal(3, 1, 50),
        "kind": ["c"] * 50,
    })

    result = evaluate_monitoring_window(
        reference_features=reference,
        current_features=current,
        reference_scores=rng.normal(0.1, 0.01, 100),
        current_scores=rng.normal(0.3, 0.02, 50),
        performance_metrics={"f1": 0.72, "false_positive_rate": 0.13},
    )
    assert result.retraining["recommended"] is True

    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    factory = create_session_factory(engine)

    with session_scope(factory) as db:
        persist_monitoring_result(
            db_session=db,
            result=result,
            model_name="model",
            dataset_name="current",
            performance_metrics={"f1": 0.72},
        )

    with session_scope(factory) as db:
        assert len(DriftRepository(db).list()) >= 1
        assert len(EvaluationRepository(db).list()) == 1
