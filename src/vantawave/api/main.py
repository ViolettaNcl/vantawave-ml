from importlib.util import find_spec

from fastapi import FastAPI, HTTPException
from vantawave.api.ai_routes import router as ai_router
from vantawave.api.wifi_recovery_routes import router as wifi_recovery_router
from vantawave.api.capture_audit_routes import router as capture_audit_router
from vantawave.api.simulation_routes import router as simulation_router
from vantawave.web.routes import router as web_router
from vantawave.core.readiness import readiness_report
from vantawave.core.logging.json_logger import configure_logging
from vantawave.core.settings import load_settings

from vantawave.api.schemas import RiskRequest, RiskResponse
from vantawave.data.awid3 import (
    AWID3_CATEGORICAL_FEATURES,
    AWID3_FEATURES,
    AWID3_NUMERIC_FEATURES,
)
from vantawave.data.schema import FEATURE_COLUMNS
from vantawave.experiments.store import FileExperimentStore
from vantawave.ml.promotion.policy import PromotionPolicy
from vantawave.lab.registry import AuthorizedTargetRegistry
from vantawave.lab.sessions import LabSessionStore
from vantawave.registry.local import LocalModelRegistry
from vantawave.risk.engine import RiskInput, calculate_risk
from vantawave.sensors.adapters.windows_netsh import WindowsNetshSensor
from vantawave.sensors.capabilities import detect_host_capabilities
from vantawave.sensors.events import EventType, WirelessEvent
from vantawave.sensors.features.window import WindowFeatures

settings = load_settings()
configure_logging(level=settings.log_level, format_name=settings.log_format)

app = FastAPI(
    title="VantaWave ML",
    version="1.1.1",
    description="Wi-Fi telemetry, ML, deep anomaly detection, MLOps and AI research platform.",
)

app.include_router(ai_router)
app.include_router(wifi_recovery_router)
app.include_router(capture_audit_router)
app.include_router(simulation_router)
app.include_router(web_router)


@app.get("/")
def root():
    return {
        "project": "VantaWave ML",
        "version": "1.1.1",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "message": "VantaWave ML API is online.",
    }


@app.get("/health")
def health():
    return {"status": "ok", "project": "VantaWave ML", "version": "1.1.1"}


@app.get("/ready")
def ready():
    report = readiness_report(
        require_database=settings.readiness_requires_database,
    )
    if not report["ready"]:
        raise HTTPException(status_code=503, detail=report)
    return report


@app.get("/config/public")
def public_config():
    return {
        "environment": settings.environment,
        "host": settings.host,
        "port": settings.port,
        "log_level": settings.log_level,
        "log_format": settings.log_format,
        "knowledge_paths": list(settings.knowledge_paths),
        "readiness_requires_database": settings.readiness_requires_database,
    }


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
        "persistent_monitoring": True,
        "database_layer": True,
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


@app.get("/lab/targets")
def lab_targets():
    return {"targets": AuthorizedTargetRegistry().list_targets()}


@app.get("/lab/sessions")
def lab_sessions():
    return {"sessions": LabSessionStore().list_sessions()}


@app.get("/lab/capabilities")
def lab_capabilities():
    return {
        "authorized_target_registry": True,
        "session_lifecycle": True,
        "before_after_comparison": True,
        "evidence_hashing": "sha256",
        "incident_generation": True,
        "active_attack_automation": False,
    }


@app.get("/data/capabilities")
def data_capabilities():
    from importlib.util import find_spec

    return {
        "sqlalchemy": find_spec("sqlalchemy") is not None,
        "alembic": find_spec("alembic") is not None,
        "psycopg": find_spec("psycopg") is not None,
        "sqlite_default": True,
        "postgresql_ready": True,
        "database_env_var": "VANTAWAVE_DATABASE_URL",
    }


@app.get("/monitoring/policy")
def monitoring_policy():
    from vantawave.monitoring.policy import EvaluationPolicy

    return EvaluationPolicy().to_dict()


@app.get("/db/health")
def database_health():
    if find_spec("sqlalchemy") is None:
        raise HTTPException(
            status_code=503,
            detail='Database extra is not installed. Use: pip install -e ".[database]"',
        )
    from sqlalchemy import text as sql_text
    from vantawave.db.config import load_database_config
    from vantawave.db.session import create_db_engine

    config = load_database_config()
    engine = create_db_engine(config)
    try:
        with engine.connect() as connection:
            connection.execute(sql_text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "status": "ok",
        "url_scheme": config.url.split(":", 1)[0],
        "postgresql": config.is_postgresql,
    }


@app.get("/monitoring/recent")
def monitoring_recent():
    if find_spec("sqlalchemy") is None:
        raise HTTPException(
            status_code=503,
            detail='Database extra is not installed. Use: pip install -e ".[database]"',
        )
    from vantawave.db.init import initialize_database
    from vantawave.db.repositories import DriftRepository, EvaluationRepository
    from vantawave.db.serialization import orm_to_dict
    from vantawave.db.session import create_session_factory, session_scope

    engine = initialize_database()
    factory = create_session_factory(engine)
    with session_scope(factory) as db:
        drift = [orm_to_dict(x) for x in DriftRepository(db).list()[:50]]
        evaluations = [orm_to_dict(x) for x in EvaluationRepository(db).list()[:20]]
    return {"drift_events": drift, "evaluations": evaluations}


@app.get("/incidents")
def incidents():
    if find_spec("sqlalchemy") is None:
        raise HTTPException(status_code=503, detail="SQLAlchemy is unavailable.")
    from vantawave.db.init import initialize_database
    from vantawave.db.repositories import IncidentRepository
    from vantawave.db.serialization import orm_to_dict
    from vantawave.db.session import create_session_factory, session_scope

    engine = initialize_database()
    factory = create_session_factory(engine)
    with session_scope(factory) as db:
        records = [orm_to_dict(item) for item in IncidentRepository(db).list()]
    return {"incidents": records[:100]}


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
