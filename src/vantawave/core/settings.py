from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    environment: str
    host: str
    port: int
    log_level: str
    log_format: str
    database_url: str | None
    knowledge_paths: tuple[str, ...]
    readiness_requires_database: bool

    def to_dict(self):
        return asdict(self)


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    knowledge = tuple(
        item.strip()
        for item in os.getenv("VANTAWAVE_KNOWLEDGE_PATHS", "docs").split(os.pathsep)
        if item.strip()
    )
    return Settings(
        environment=os.getenv("VANTAWAVE_ENV", "development"),
        host=os.getenv("VANTAWAVE_HOST", "127.0.0.1"),
        port=int(os.getenv("VANTAWAVE_PORT", "8000")),
        log_level=os.getenv("VANTAWAVE_LOG_LEVEL", "INFO").upper(),
        log_format=os.getenv("VANTAWAVE_LOG_FORMAT", "json").lower(),
        database_url=os.getenv("VANTAWAVE_DATABASE_URL"),
        knowledge_paths=knowledge,
        readiness_requires_database=_bool_env(
            "VANTAWAVE_READINESS_REQUIRES_DATABASE",
            default=False,
        ),
    )
