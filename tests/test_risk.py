from vantawave.risk.engine import RiskInput, calculate_risk

def test_low_risk_is_info():
    result = calculate_risk(RiskInput(0.05, 0.10))
    assert result.score < 20
    assert result.severity == "INFO"

def test_high_risk_increases_with_evidence():
    low = calculate_risk(RiskInput(0.2, 0.2))
    high = calculate_risk(RiskInput(0.95, 0.95, repeated_alerts=8, unknown_device=True))
    assert high.score > low.score
    assert high.severity in {"HIGH", "CRITICAL"}
