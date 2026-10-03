from __future__ import annotations

import argparse
import json
from pathlib import Path

from vantawave.db.init import initialize_database
from vantawave.db.repositories import SensorSessionRepository, TargetRepository
from vantawave.db.session import create_session_factory, session_scope


def load_json(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--targets",
        type=Path,
        default=Path("artifacts/lab/targets.json"),
    )
    parser.add_argument(
        "--sessions",
        type=Path,
        default=Path("artifacts/lab/sessions.json"),
    )
    args = parser.parse_args()

    targets_payload = load_json(args.targets)
    sessions_payload = load_json(args.sessions)

    engine = initialize_database()
    factory = create_session_factory(engine)

    with session_scope(factory) as db:
        target_repo = TargetRepository(db)
        for target in targets_payload.get("targets", []):
            target_repo.upsert(target)

        session_repo = SensorSessionRepository(db)
        for session in sessions_payload.get("sessions", []):
            session_repo.upsert(session)

    print(
        f"Imported {len(targets_payload.get('targets', []))} target(s) and "
        f"{len(sessions_payload.get('sessions', []))} session(s)."
    )


if __name__ == "__main__":
    main()
