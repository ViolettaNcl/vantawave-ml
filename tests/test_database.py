from sqlalchemy import create_engine

from vantawave.db.base import Base
from vantawave.db.repositories import (
    DriftRepository,
    EvaluationRepository,
    IncidentRepository,
    ModelSnapshotRepository,
    SensorSessionRepository,
    TargetRepository,
)
from vantawave.db.session import create_session_factory, session_scope


def make_factory():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return create_session_factory(engine)


def test_database_repositories_roundtrip():
    factory = make_factory()

    with session_scope(factory) as db:
        target = TargetRepository(db).upsert({
            "target_id": "target1",
            "name": "Lab",
            "ssid": "Lab",
            "bssid": "00:11:22:33:44:55",
            "authorized": True,
            "owner_confirmation": "Authorized laboratory AP.",
        })
        SensorSessionRepository(db).upsert({
            "session_id": "session1",
            "target_id": "target1",
            "source": "test",
            "mode": "passive",
            "status": "completed",
            "event_count": 10,
        })
        IncidentRepository(db).add(
            incident_id="incident1",
            title="test",
            severity="MEDIUM",
            risk_score=50,
            session_id="session1",
            target_id="target1",
            evidence={"x": 1},
        )
        DriftRepository(db).add(
            drift_id="drift1",
            feature="event_rate",
            kind="numeric_mean_shift_z",
            score=1.5,
            severity="warning",
        )
        ModelSnapshotRepository(db).add(
            snapshot_id="model1",
            model_name="demo",
            model_version="1",
            alias="champion",
            threshold=0.5,
            metrics={"f1": 0.9},
        )
        EvaluationRepository(db).add(
            evaluation_id="eval1",
            model_name="demo",
            dataset_name="test",
            metrics={"f1": 0.9},
            recommendation="keep_current_model",
            reasons=["ok"],
        )
        assert target.authorized is True

    with session_scope(factory) as db:
        assert len(TargetRepository(db).list()) == 1
        assert len(SensorSessionRepository(db).list()) == 1
        assert len(IncidentRepository(db).list()) == 1
        assert len(DriftRepository(db).list()) == 1
        assert len(ModelSnapshotRepository(db).list()) == 1
        assert len(EvaluationRepository(db).list()) == 1
