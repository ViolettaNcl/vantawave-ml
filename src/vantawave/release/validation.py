from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from importlib.util import find_spec


@dataclass(frozen=True)
class ReleaseCheck:
    name: str
    ok: bool
    detail: str

    def to_dict(self):
        return asdict(self)


def validate_release(root: str | Path = ".") -> list[ReleaseCheck]:
    root = Path(root)
    required_files = [
        "README.md",
        "README_RU.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/ISSUE_TEMPLATE/bug_report.md",
        ".github/ISSUE_TEMPLATE/feature_request.md",
        "SECURITY.md",
        "PROJECT_PROMPT.md",
        "ROADMAP.md",
        "Dockerfile",
        "docker-compose.yml",
        ".env.example",
        "alembic.ini",
        "src/vantawave/web/index.html",
        "src/vantawave/web/app.css",
        "src/vantawave/web/app.js",
        "docs/ai_security_analyst.md",
        "docs/production.md",
        "docs/database.md",
        "docs/deep_anomaly_detection.md",
        "docs/passive_sensor.md",
        "docs/wifi_recovery.md",
        "docs/authorized_capture_audit.md",
        "src/vantawave/capture_audit/analyzer.py",
        "src/vantawave/capture_audit/aircrack.py",
        "src/vantawave/api/capture_audit_routes.py",
        "src/vantawave/api/simulation_routes.py",
        "src/vantawave/simulation/scenarios.py",
        "src/vantawave/simulation/engine.py",
        "docs/adversary_simulation.md",
        "docs/portfolio_showcase.md",
        "docs/assets/vantawave-hero.gif",
        "docs/assets/adversary-simulation.gif",
        "README_RU.md",
        "src/vantawave/wifi_recovery/windows.py",
        "src/vantawave/api/wifi_recovery_routes.py",
    ]

    checks = []
    for rel in required_files:
        path = root / rel
        checks.append(
            ReleaseCheck(
                name=f"file:{rel}",
                ok=path.exists(),
                detail="present" if path.exists() else "missing",
            )
        )

    env_path = root / ".env"
    checks.append(
        ReleaseCheck(
            name="secret-hygiene:.env",
            ok=not env_path.exists(),
            detail="not committed" if not env_path.exists() else "remove .env before release",
        )
    )

    for module in ("fastapi", "sklearn", "sqlalchemy"):
        available = find_spec(module) is not None
        checks.append(
            ReleaseCheck(
                name=f"dependency:{module}",
                ok=available,
                detail="available" if available else "missing",
            )
        )

    return checks
