from vantawave.lab.incidents import generate_lab_incident

def test_lab_incident_has_risk():
    incident = generate_lab_incident(
        session_id="s1",
        target_id="t1",
        anomaly_score=0.9,
        classifier_confidence=0.8,
        repeated_alerts=2,
        unknown_device=True,
        evidence={"x": 1},
    )
    assert incident.risk_score > 0
    assert incident.severity in {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
