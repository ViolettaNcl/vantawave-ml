from vantawave.ai.analyst.similarity import similar_incidents


def test_similar_incidents_ranks_related_history():
    target = {
        "incident_id": "a",
        "title": "authentication anomaly",
        "severity": "HIGH",
        "predicted_class": "authentication_anomaly",
        "evidence_json": {"auth_rate": 10},
    }
    history = [
        {
            "incident_id": "b",
            "title": "previous authentication anomaly",
            "severity": "MEDIUM",
            "predicted_class": "authentication_anomaly",
            "evidence_json": {"auth_rate": 8},
        },
        {
            "incident_id": "c",
            "title": "database maintenance",
            "severity": "LOW",
            "predicted_class": "maintenance",
            "evidence_json": {"migration": True},
        },
    ]
    result = similar_incidents(target, history, top_k=2)
    assert result
    assert result[0]["incident_id"] == "b"
