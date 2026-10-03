from dataclasses import dataclass

@dataclass(frozen=True)
class RiskInput:
    anomaly_score: float
    classifier_confidence: float
    repeated_alerts: int = 0
    unknown_device: bool = False

@dataclass(frozen=True)
class RiskResult:
    score: int
    severity: str
    components: dict[str, float]

def calculate_risk(value: RiskInput) -> RiskResult:
    anomaly = max(0.0, min(1.0, value.anomaly_score)) * 45.0
    confidence = max(0.0, min(1.0, value.classifier_confidence)) * 30.0
    repetition = min(max(value.repeated_alerts, 0), 10) / 10 * 15.0
    unknown = 10.0 if value.unknown_device else 0.0

    total = int(round(min(100.0, anomaly + confidence + repetition + unknown)))

    if total >= 85:
        severity = "CRITICAL"
    elif total >= 70:
        severity = "HIGH"
    elif total >= 45:
        severity = "MEDIUM"
    elif total >= 20:
        severity = "LOW"
    else:
        severity = "INFO"

    return RiskResult(
        score=total,
        severity=severity,
        components={
            "anomaly": anomaly,
            "classifier_confidence": confidence,
            "repeated_alerts": repetition,
            "unknown_device": unknown,
        },
    )
