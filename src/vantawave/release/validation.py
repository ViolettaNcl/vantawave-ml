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
