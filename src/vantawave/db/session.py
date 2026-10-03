from __future__ import annotations

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from vantawave.db.config import DatabaseConfig, load_database_config


def create_db_engine(config: DatabaseConfig | None = None):
    config = config or load_database_config()
    kwargs = {"echo": config.echo, "future": True}
    if config.url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(config.url, **kwargs)


def create_session_factory(engine=None):
    engine = engine or create_db_engine()
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@contextmanager
def session_scope(session_factory=None):
    session_factory = session_factory or create_session_factory()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
