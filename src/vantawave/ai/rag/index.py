from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from vantawave.ai.rag.chunking import chunk_document
from vantawave.ai.rag.documents import KnowledgeChunk, KnowledgeDocument, load_text_document
from vantawave.ai.rag.retrieval import TfidfRetriever


SUPPORTED_TEXT_SUFFIXES = {".md", ".txt", ".rst"}


@dataclass
class KnowledgeIndex:
    documents: list[KnowledgeDocument]
    chunks: list[KnowledgeChunk]

    @classmethod
    def from_paths(cls, paths: list[str | Path]):
        documents = []
        for raw in paths:
            path = Path(raw)
            if path.is_dir():
                candidates = sorted(
                    p for p in path.rglob("*")
                    if p.is_file() and p.suffix.lower() in SUPPORTED_TEXT_SUFFIXES
                )
            else:
                candidates = [path]

            for candidate in candidates:
                if candidate.suffix.lower() not in SUPPORTED_TEXT_SUFFIXES:
                    continue
                documents.append(load_text_document(candidate))

        chunks = []
        for document in documents:
            chunks.extend(chunk_document(document))
        return cls(documents=documents, chunks=chunks)

    def tfidf(self):
        return TfidfRetriever(self.chunks)

    def save_manifest(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "documents": [doc.to_dict() for doc in self.documents],
            "chunks": [chunk.to_dict() for chunk in self.chunks],
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path
