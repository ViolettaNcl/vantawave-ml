from pydantic import BaseModel, Field

class RiskRequest(BaseModel):
    anomaly_score: float = Field(ge=0, le=1)
    classifier_confidence: float = Field(ge=0, le=1)
    repeated_alerts: int = Field(default=0, ge=0)
    unknown_device: bool = False

class RiskResponse(BaseModel):
    score: int
    severity: str
    components: dict[str, float]
