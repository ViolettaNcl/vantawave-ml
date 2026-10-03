from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import uuid


def sha256_file(path: str | Path) -> str:
    path = Path(path)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class EvidenceItem:
    kind: str
    path: str
    sha256: str
    size_bytes: int

    def to_dict(self):
        return asdict(self)


@dataclass
class EvidenceBundle:
    session_id: str
    target_id: str
    items: list[EvidenceItem]
    bundle_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self):
        return {
            "bundle_id": self.bundle_id,
            "session_id": self.session_id,
            "target_id": self.target_id,
            "created_at": self.created_at,
            "items": [item.to_dict() for item in self.items],
        }


def build_evidence_bundle(
    *,
    session_id: str,
    target_id: str,
    files: dict[str, str | Path],
    output: str | Path | None = None,
) -> EvidenceBundle:
    items = []
    for kind, path in files.items():
        path = Path(path)
        if not path.exists():
            continue
        items.append(
            EvidenceItem(
                kind=kind,
                path=str(path),
                sha256=sha256_file(path),
                size_bytes=path.stat().st_size,
            )
        )

    bundle = EvidenceBundle(
        session_id=session_id,
        target_id=target_id,
        items=items,
    )

    if output is not None:
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(bundle.to_dict(), indent=2), encoding="utf-8")

    return bundle
