from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class DatabaseConfig:
    url: str
    echo: bool = False

    @property
    def is_postgresql(self) -> bool:
        return self.url.startswith("postgresql")


def default_database_url() -> str:
    env = os.getenv("VANTAWAVE_DATABASE_URL")
    if env:
        return env

    db_path = Path("artifacts/v09/vantawave.db").resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.as_posix()}"


def load_database_config() -> DatabaseConfig:
    echo = os.getenv("VANTAWAVE_DB_ECHO", "").strip().lower() in {"1", "true", "yes"}
    return DatabaseConfig(url=default_database_url(), echo=echo)
