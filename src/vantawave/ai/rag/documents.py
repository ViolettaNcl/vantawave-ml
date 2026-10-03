from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import hashlib
import json
import uuid


@dataclass(frozen=True)
class KnowledgeDocument:
    document_id: str
    title: str
    source: str
    text: str
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class KnowledgeChunk:
    chunk_id: str
    document_id: str
    title: str
    source: str
    text: str
    start_char: int
    end_char: int
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

    @property
    def citation(self) -> str:
        return f"[{self.chunk_id}]"


def stable_document_id(source: str, text: str) -> str:
    digest = hashlib.sha256(f"{source}\n{text}".encode("utf-8")).hexdigest()
    return digest[:16]


def load_text_document(path: str | Path, *, title: str | None = None) -> KnowledgeDocument:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    source = str(path)
    return KnowledgeDocument(
        document_id=stable_document_id(source, text),
        title=title or path.stem,
        source=source,
        text=text,
        metadata={"suffix": path.suffix.lower()},
    )


def save_documents(documents: list[KnowledgeDocument], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([doc.to_dict() for doc in documents], indent=2),
        encoding="utf-8",
    )
    return path
