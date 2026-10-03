from pathlib import Path
import json
from vantawave.lab.comparison import compare_feature_windows
from vantawave.lab.evidence import build_evidence_bundle
from vantawave.lab.incidents import generate_lab_incident
from vantawave.lab.registry import AuthorizedTarget, AuthorizedTargetRegistry
from vantawave.lab.reporting import save_lab_report
from vantawave.lab.sessions import LabSessionStore

def main():
    root = Path("artifacts/lab/demo")
    registry = AuthorizedTargetRegistry(root / "targets.json")
    target = AuthorizedTarget(
        name="VantaWave Lab AP",
        ssid="VantaWave-Lab",
        bssid="00:11:22:33:44:55",
        authorized=True,
        owner_confirmation="I own or am explicitly authorized to test this lab AP.",
    )
    registry.register(target)

    sessions = LabSessionStore(root / "sessions.json", registry)
    session = sessions.create(
        target_id=target.target_id,
        mode="passive-before-after",
        sensor_source="normalized-fixture",
    )
    sessions.start(session.session_id)

    before = {
        "auth_rate": 0.02,
        "deauth_rate": 0.00,
        "event_rate": 0.30,
        "unique_bssids": 1.0,
    }
    after = {
        "auth_rate": 0.10,
        "deauth_rate": 0.03,
        "event_rate": 0.60,
        "unique_bssids": 1.0,
    }
    session = sessions.complete(
        session.session_id,
        before_features=before,
        after_features=after,
    )

    evidence_file = root / "evidence.txt"
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text("Authorized lab demo evidence.", encoding="utf-8")
    bundle = build_evidence_bundle(
        session_id=session.session_id,
        target_id=target.target_id,
        files={"demo": evidence_file},
        output=root / "evidence_bundle.json",
    )

    incident = generate_lab_incident(
        session_id=session.session_id,
        target_id=target.target_id,
        anomaly_score=0.78,
        classifier_confidence=0.74,
        repeated_alerts=2,
        unknown_device=False,
        evidence={"feature_changes": [x.to_dict() for x in compare_feature_windows(before, after)]},
    )

    payload = {
        "target": target.to_dict(),
        "session": session.to_dict(),
        "feature_deltas": [x.to_dict() for x in compare_feature_windows(before, after)],
        "incidents": [incident.to_dict()],
        "evidence_bundle": bundle.to_dict(),
    }
    json_path, md_path = save_lab_report(payload, root / "report")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")
    print(json.dumps(payload["incidents"], indent=2))

if __name__ == "__main__":
    main()
