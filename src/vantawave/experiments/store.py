from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import uuid

@dataclass
class ExperimentRun:
    name: str
    version: str
    params: dict
    metrics: dict
    artifacts: dict = field(default_factory=dict)
    dataset: dict = field(default_factory=dict)
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class FileExperimentStore:
    def __init__(self, root: str | Path = "artifacts/experiments"):
        self.root = Path(root)

    def save(self, run: ExperimentRun) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / f"{run.run_id}.json"
        path.write_text(json.dumps(asdict(run), indent=2), encoding="utf-8")
        return path

    def list_runs(self) -> list[dict]:
        if not self.root.exists():
            return []
        return [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(self.root.glob("*.json"))
        ]
