from __future__ import annotations

from vantawave.db.base import Base
from vantawave.db.session import create_db_engine


def initialize_database(engine=None):
    engine = engine or create_db_engine()
    Base.metadata.create_all(engine)
    return engine
