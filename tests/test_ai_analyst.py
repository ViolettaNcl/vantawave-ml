from vantawave.ai.analyst.grounded import build_grounded_report
from vantawave.ai.analyst.guards import validate_response_citations
from vantawave.ai.analyst.prompts import build_grounded_prompt


def incident():
    return {
        "incident_id": "inc-1",
        "title": "Authorized lab anomaly",
        "severity": "HIGH",
        "risk_score": 82,
        "anomaly_score": 0.91,
        "predicted_class": "authentication_anomaly",
        "confidence": 0.87,
        "evidence_json": {"auth_rate_change_percent": 380},
    }


def test_grounded_report_restates_persisted_evidence():
    report = build_grounded_report(incident=incident())
    payload = report.to_dict()

    assert payload["incident_id"] == "inc-1"
    assert payload["findings"]
    assert any("[incident:inc-1]" in finding["citations"] for finding in payload["findings"])
    assert any(item["citation"] == "[evidence:inc-1]" for item in payload["evidence"])


def test_prompt_and_citation_guard():
    report = build_grounded_report(incident=incident()).to_dict()
    prompt = build_grounded_prompt(
        report,
        question="What does the incident evidence show?",
    )
    assert "[incident:inc-1]" in prompt.user

    valid = validate_response_citations(
        "The risk score is recorded in the incident. [incident:inc-1]",
        allowed_citations=prompt.allowed_citations,
    )
    assert valid.valid

    invalid = validate_response_citations(
        "Unsupported claim. [incident:not-real]",
        allowed_citations=prompt.allowed_citations,
    )
    assert not invalid.valid
