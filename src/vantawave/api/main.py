from importlib.util import find_spec

from fastapi import FastAPI, HTTPException

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
from vantawave.sensors.adapters.windows_netsh import WindowsNetshSensor
from vantawave.sensors.capabilities import detect_host_capabilities
from vantawave.sensors.events import EventType, WirelessEvent
from vantawave.sensors.features.window import WindowFeatures

app = FastAPI(
    title="VantaWave ML",
    version="0.7.0",
    description="Wi-Fi telemetry, ML, deep anomaly detection, MLOps and AI research platform.",
)


@app.get("/")
def root():
    return {
        "project": "VantaWave ML",
        "version": "0.7.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "message": "VantaWave ML API is online.",
    }


@app.get("/health")
def health():
    return {"status": "ok", "project": "VantaWave ML", "version": "0.7.0"}


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
        "anomaly_detection": [
            "isolation_forest",
            "pytorch_autoencoder",
        ],
        "optional": [
            "catboost",
            "shap",
            "mlflow",
            "torch",
            "scapy",
        ],
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
        "torch": find_spec("torch") is not None,
        "scapy": find_spec("scapy") is not None,
        "local_registry": True,
        "threshold_calibration": True,
        "error_analysis": True,
        "model_promotion": True,
        "deep_anomaly_detection": True,
        "drift_baseline": True,
    }


@app.get("/deep/capabilities")
def deep_capabilities():
    return {
        "torch_available": find_spec("torch") is not None,
        "normal_only_training": True,
        "reconstruction_threshold": "validation-normal-quantile",
        "baseline_model": "isolation_forest",
        "known_unknown_attack_evaluation": True,
    }


@app.get("/sensors/capabilities")
def sensor_capabilities():
    host = detect_host_capabilities()
    windows = WindowsNetshSensor().capability()
    return {
        "host": host.to_dict(),
        "adapters": [
            windows.to_dict(),
            {
                "name": "pcap-replay",
                "available": host.pcap_replay,
                "mode": "offline-pcap-replay",
                "reason": None if host.pcap_replay else "Install the optional pcap extra.",
            },
        ],
    }


@app.get("/sensors/schema")
def sensor_schema():
    return {
        "event_types": [item.value for item in EventType],
        "event_fields": list(WirelessEvent.__dataclass_fields__.keys()),
        "window_feature_fields": list(WindowFeatures.__dataclass_fields__.keys()),
        "live_raw_80211_capture": False,
        "note": (
            "v0.7 supports OS-visible Windows WLAN discovery and offline PCAP replay. "
            "Raw live 802.11 monitor-mode capture is intentionally deferred to authorized lab work."
        ),
    }


@app.get("/sensors/windows/scan")
def windows_sensor_scan():
    sensor = WindowsNetshSensor()
    capability = sensor.capability()
    if not capability.available:
        raise HTTPException(
            status_code=503,
            detail=capability.reason or "Windows WLAN discovery is unavailable.",
        )

    try:
        events = sensor.collect_once()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "source": sensor.name,
        "count": len(events),
        "events": [event.to_dict() for event in events],
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
