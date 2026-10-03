from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from vantawave.ai.analyst.service import SecurityAnalystService
from vantawave.core.settings import load_settings
from vantawave.db.init import initialize_database
from vantawave.db.repositories import IncidentRepository
from vantawave.db.serialization import orm_to_dict
from vantawave.db.session import create_session_factory, session_scope


router = APIRouter(prefix="/ai", tags=["AI Security Analyst"])


@router.get("/capabilities")
def ai_capabilities():
    settings = load_settings()
    return {
        "grounded_analyst": True,
        "tfidf_rag": True,
        "semantic_embeddings_optional": True,
        "historical_incident_similarity": True,
        "citations": True,
        "restricted_actions": [
            "summarize_incident",
            "retrieve_project_knowledge",
            "compare_historical_incidents",
            "suggest_defensive_checks",
        ],
        "forbidden_autonomous_actions": [
            "packet_injection",
            "credential_theft",
            "third_party_targeting",
            "active_attack_execution",
        ],
        "knowledge_paths": list(settings.knowledge_paths),
    }


@router.get("/analyze/{incident_id}")
def analyze_incident(
    incident_id: str,
    query: str | None = Query(default=None),
):
    settings = load_settings()
    engine = initialize_database()
    factory = create_session_factory(engine)

    with session_scope(factory) as db:
        repository = IncidentRepository(db)
        record = repository.get(incident_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Incident not found.")

        incident = orm_to_dict(record)
        historical = [
            orm_to_dict(item)
            for item in repository.list()
            if item.incident_id != incident_id
        ]

    analyst = SecurityAnalystService(
        knowledge_paths=list(settings.knowledge_paths),
        top_k=5,
    )
    report = analyst.analyze(
        incident=incident,
        historical_incidents=historical,
        query=query,
    )
    return report.to_dict()
