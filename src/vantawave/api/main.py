from fastapi import FastAPI
from vantawave.api.schemas import RiskRequest, RiskResponse
from vantawave.data.schema import FEATURE_COLUMNS
from vantawave.risk.engine import RiskInput, calculate_risk

app = FastAPI(
    title="VantaWave ML",
    version="0.3.0",
    description="Wi-Fi security and machine-learning research platform.",
)

@app.get("/")
def root():
    return {
        "project": "VantaWave ML",
        "version": "0.3.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "message": "VantaWave ML API is online.",
    }

@app.get("/health")
def health():
    return {"status": "ok", "project": "VantaWave ML", "version": "0.3.0"}

@app.get("/features")
def features():
    return {"count": len(FEATURE_COLUMNS), "features": FEATURE_COLUMNS}

@app.get("/models")
def models():
    return {
        "classification": [
            "logistic_regression",
            "random_forest",
            "hist_gradient_boosting",
        ],
        "anomaly_detection": ["isolation_forest"],
        "optional": ["catboost"],
    }

@app.post("/risk/score", response_model=RiskResponse)
def risk_score(request: RiskRequest):
    result = calculate_risk(RiskInput(
        anomaly_score=request.anomaly_score,
        classifier_confidence=request.classifier_confidence,
        repeated_alerts=request.repeated_alerts,
        unknown_device=request.unknown_device,
    ))
    return RiskResponse(
        score=result.score,
        severity=result.severity,
        components=result.components,
    )
