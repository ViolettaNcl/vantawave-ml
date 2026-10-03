from vantawave.lab.registry import AuthorizedTarget, AuthorizedTargetRegistry
from vantawave.lab.sessions import LabSessionStatus, LabSessionStore

def test_lab_session_lifecycle(tmp_path):
    registry = AuthorizedTargetRegistry(tmp_path / "targets.json")
    target = registry.register(
        AuthorizedTarget(
            name="Lab",
            ssid="Lab",
            bssid="00:11:22:33:44:55",
            authorized=True,
            owner_confirmation="I own this lab AP and authorize testing.",
        )
    )
    store = LabSessionStore(tmp_path / "sessions.json", registry)
    session = store.create(target_id=target.target_id, mode="passive", sensor_source="test")
    assert session.status == LabSessionStatus.CREATED

    session = store.start(session.session_id)
    assert session.status == LabSessionStatus.RUNNING

    session = store.complete(
        session.session_id,
        before_features={"event_rate": 1.0},
        after_features={"event_rate": 2.0},
    )
    assert session.status == LabSessionStatus.COMPLETED
