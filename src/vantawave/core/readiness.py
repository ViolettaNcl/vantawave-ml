from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib.util import find_spec


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str

    def to_dict(self):
        return asdict(self)


def dependency_check(module_name: str, *, required: bool = False) -> CheckResult:
    available = find_spec(module_name) is not None
    return CheckResult(
        name=f"dependency:{module_name}",
        ok=available or not required,
        detail="available" if available else ("missing-required" if required else "missing-optional"),
    )


def database_check(*, required: bool = False) -> CheckResult:
    if find_spec("sqlalchemy") is None:
        return CheckResult(
            name="database",
            ok=not required,
            detail="sqlalchemy-not-installed",
        )
    try:
        from sqlalchemy import text
        from vantawave.db.config import load_database_config
        from vantawave.db.session import create_db_engine

        engine = create_db_engine(load_database_config())
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return CheckResult(name="database", ok=True, detail="reachable")
    except Exception as exc:
        return CheckResult(
            name="database",
            ok=not required,
            detail=f"unavailable:{type(exc).__name__}",
        )


def readiness_report(*, require_database: bool = False) -> dict:
    checks = [
        database_check(required=require_database),
        dependency_check("sklearn", required=True),
        dependency_check("fastapi", required=True),
        dependency_check("torch", required=False),
        dependency_check("mlflow", required=False),
        dependency_check("shap", required=False),
        dependency_check("scapy", required=False),
    ]
    return {
        "ready": all(check.ok for check in checks),
        "checks": [check.to_dict() for check in checks],
    }
