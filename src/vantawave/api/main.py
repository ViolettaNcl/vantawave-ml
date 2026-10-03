from importlib.util import find_spec

from fastapi import FastAPI

from vantawave.api.schemas import RiskRequest, RiskResponse
from vantawave.data.awid3 import (
    AWID3_CATEGORICAL_FEATURES,
    AWID3_FEATURES,
    AWID3_NUMERIC_FEATURES,
)
from vantawave.data.schema import FEATURE_COLUMNS
from vantawave.experiments.store import FileExperimentStore
from vantawave.ml.promotion.policy import PromotionPolicy
from vantawave.registry.local import LocalModelRegistry
from vantawave.risk.engine import RiskInput, calculate_risk

app = FastAPI(
    title="VantaWave ML",
    version="0.5.0",
    description="Wi-Fi security, ML, MLOps and AI research platform.",
)


@app.get("/")
def root():
    return {
        "project": "VantaWave ML",
        "version": "0.5.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "message": "VantaWave ML API is online.",
    }


@app.get("/health")
def health():
    return {"status": "ok", "project": "VantaWave ML", "version": "0.5.0"}


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
        "research_awid3": [
            "logistic_regression",
            "random_forest",
        ],
        "anomaly_detection": ["isolation_forest"],
        "optional": ["catboost", "shap", "mlflow"],
    }


@app.get("/research/awid3/schema")
def awid3_schema():
    return {
        "feature_count": len(AWID3_FEATURES),
        "numeric": AWID3_NUMERIC_FEATURES,
        "categorical": AWID3_CATEGORICAL_FEATURES,
    }


@app.get("/mlops/capabilities")
def mlops_capabilities():
    return {
        "mlflow": find_spec("mlflow") is not None,
        "shap": find_spec("shap") is not None,
        "local_registry": True,
        "threshold_calibration": True,
        "error_analysis": True,
        "model_promotion": True,
    }


@app.get("/registry/models")
def registry_models():
    registry = LocalModelRegistry("artifacts/v05/registry")
    return {"models": registry.list_models()}


@app.get("/experiments")
def experiments():
    store = FileExperimentStore("artifacts/v05/experiments")
    return {"runs": store.list_runs()}


@app.get("/promotion/policy")
def promotion_policy():
    return PromotionPolicy().to_dict()


@app.post("/risk/score", response_model=RiskResponse)
def risk_score(request: RiskRequest):
    result = calculate_risk(
        RiskInput(
            anomaly_score=request.anomaly_score,
            classifier_confidence=request.classifier_confidence,
            repeated_alerts=request.repeated_alerts,
            unknown_device=request.unknown_device,
        )
    )
    return RiskResponse(
        score=result.score,
        severity=result.severity,
        components=result.components,
    )
