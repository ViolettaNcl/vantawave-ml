from __future__ import annotations


from vantawave.db.init import initialize_database
from vantawave.db.repositories import (
    DriftRepository,
    EvaluationRepository,
    IncidentRepository,
    ModelSnapshotRepository,
    SensorSessionRepository,
    TargetRepository,
)
from vantawave.db.session import create_session_factory, session_scope


def main():
    engine = initialize_database()
    factory = create_session_factory(engine)

    target_id = "portfolio-lab"
    session_id = "portfolio-session"

    with session_scope(factory) as db:
        TargetRepository(db).upsert(
            {
                "target_id": target_id,
                "name": "VantaWave Demo Lab",
                "ssid": "VantaWave-Lab",
                "bssid": "02:11:22:33:44:55",
                "authorized": True,
                "owner_confirmation": "Portfolio demo target owned/authorized by operator.",
                "notes": "Synthetic/local dashboard demonstration record.",
            }
        )
        SensorSessionRepository(db).upsert(
            {
                "session_id": session_id,
                "target_id": target_id,
                "source": "portfolio-seed",
                "mode": "passive-demo",
                "status": "completed",
                "event_count": 128,
                "metadata": {"portfolio_demo": True},
            }
        )

        incident_repo = IncidentRepository(db)
        if not incident_repo.get("portfolio-incident"):
            incident_repo.add(
                incident_id="portfolio-incident",
                title="Authorized lab authentication anomaly",
                severity="HIGH",
                risk_score=82,
                session_id=session_id,
                target_id=target_id,
                anomaly_score=0.91,
                predicted_class="authentication_anomaly",
                confidence=0.87,
                evidence={
                    "auth_rate_change_percent": 380,
                    "deauth_rate_change_percent": 160,
                    "authorized_target": True,
                    "portfolio_demo": True,
                },
            )

        drift_repo = DriftRepository(db)
        existing_drift = drift_repo.list()
        if not existing_drift:
            for feature, score, severity in [
                ("auth_rate", 2.8, "high"),
                ("deauth_rate", 1.6, "warning"),
                ("anomaly_score", 2.2, "high"),
            ]:
                drift_repo.add(
                    feature=feature,
                    kind="portfolio_demo_shift",
                    score=score,
                    severity=severity,
                    baseline_version="portfolio-v1",
                    metadata={"portfolio_demo": True},
                )

        if not ModelSnapshotRepository(db).list("vantawave-demo"):
            ModelSnapshotRepository(db).add(
                model_name="vantawave-demo",
                model_version="1.0.0",
                alias="champion",
                threshold=0.52,
                metrics={
                    "f1": 0.88,
                    "precision": 0.91,
                    "recall": 0.86,
                    "false_positive_rate": 0.05,
                },
                metadata={"portfolio_demo": True},
            )

        if not EvaluationRepository(db).list():
            EvaluationRepository(db).add(
                model_name="vantawave-demo",
                dataset_name="portfolio-demo",
                metrics={"f1": 0.88, "false_positive_rate": 0.05},
                recommendation="keep_current_model",
                reasons=["Demo model is inside configured guardrails."],
                evaluation_id="portfolio-eval",
            )

    print("Portfolio dashboard demo data seeded.")
    print("Incident ID: portfolio-incident")
    print("Open: http://127.0.0.1:8000/dashboard")


if __name__ == "__main__":
    main()
