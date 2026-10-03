from __future__ import annotations

import json
import uuid

from vantawave.ai.analyst.service import SecurityAnalystService
from vantawave.db.init import initialize_database
from vantawave.db.repositories import IncidentRepository
from vantawave.db.serialization import orm_to_dict
from vantawave.db.session import create_session_factory, session_scope


def main():
    engine = initialize_database()
    factory = create_session_factory(engine)

    incident_id = uuid.uuid4().hex[:12]
    with session_scope(factory) as db:
        repository = IncidentRepository(db)
        current = repository.add(
            incident_id=incident_id,
            title="Authorized lab authentication anomaly",
            severity="HIGH",
            risk_score=82,
            anomaly_score=0.91,
            predicted_class="authentication_anomaly",
            confidence=0.87,
            evidence={
                "auth_rate_change_percent": 380,
                "deauth_rate_change_percent": 160,
                "authorized_target": True,
            },
        )
        repository.add(
            incident_id=uuid.uuid4().hex[:12],
            title="Previous authentication anomaly",
            severity="MEDIUM",
            risk_score=58,
            anomaly_score=0.67,
            predicted_class="authentication_anomaly",
            confidence=0.71,
            evidence={"auth_rate_change_percent": 250},
        )
        current_payload = orm_to_dict(current)
        history = [orm_to_dict(item) for item in repository.list()]

    analyst = SecurityAnalystService(knowledge_paths=["docs"])
    report = analyst.analyze(
        incident=current_payload,
        historical_incidents=history,
        query="authentication anomaly defensive investigation",
    )
    print(json.dumps(report.to_dict(), indent=2))


if __name__ == "__main__":
    main()
