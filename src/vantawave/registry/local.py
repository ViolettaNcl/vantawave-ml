from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil
import uuid


@dataclass
class RegistryEntry:
    model_name: str
    version: int
    model_id: str
    artifact_path: str
    sha256: str
    metrics: dict
    threshold: float
    status: str = "candidate"
    aliases: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self):
        return asdict(self)


class LocalModelRegistry:
    def __init__(self, root: str | Path = "artifacts/registry"):
        self.root = Path(root)
        self.manifest = self.root / "registry.json"
        self.models_dir = self.root / "models"

    def _load(self) -> dict:
        if not self.manifest.exists():
            return {"models": []}
        return json.loads(self.manifest.read_text(encoding="utf-8"))

    def _save(self, payload: dict) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def list_models(self, model_name: str | None = None) -> list[dict]:
        models = self._load()["models"]
        if model_name is None:
            return models
        return [item for item in models if item["model_name"] == model_name]

    def register(
        self,
        *,
        model_name: str,
        artifact_path: str | Path,
        metrics: dict,
        threshold: float,
        metadata: dict | None = None,
        status: str = "candidate",
    ) -> RegistryEntry:
        source = Path(artifact_path)
        if not source.exists():
            raise FileNotFoundError(source)

        payload = self._load()
        existing = [
            item for item in payload["models"]
            if item["model_name"] == model_name
        ]
        version = max([int(item["version"]) for item in existing], default=0) + 1

        target_dir = self.models_dir / model_name
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"v{version}.joblib"
        shutil.copy2(source, target)

        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        entry = RegistryEntry(
            model_name=model_name,
            version=version,
            model_id=uuid.uuid4().hex[:12],
            artifact_path=str(target),
            sha256=digest,
            metrics=dict(metrics),
            threshold=float(threshold),
            status=status,
            metadata=dict(metadata or {}),
        )
        payload["models"].append(entry.to_dict())
        self._save(payload)
        return entry

    def set_alias(self, model_name: str, version: int, alias: str) -> dict:
        payload = self._load()
        target = None

        for item in payload["models"]:
            if item["model_name"] != model_name:
                continue
            aliases = [a for a in item.get("aliases", []) if a != alias]
            item["aliases"] = aliases
            if int(item["version"]) == int(version):
                target = item

        if target is None:
            raise KeyError(f"{model_name} v{version} not found.")

        target.setdefault("aliases", []).append(alias)
        self._save(payload)
        return target

    def promote_to_champion(self, model_name: str, version: int) -> dict:
        payload = self._load()
        target = None
        for item in payload["models"]:
            if item["model_name"] != model_name:
                continue
            if item.get("status") == "champion":
                item["status"] = "archived"
            item["aliases"] = [a for a in item.get("aliases", []) if a != "champion"]
            if int(item["version"]) == int(version):
                target = item

        if target is None:
            raise KeyError(f"{model_name} v{version} not found.")

        target["status"] = "champion"
        target.setdefault("aliases", []).append("champion")
        self._save(payload)
        return target
