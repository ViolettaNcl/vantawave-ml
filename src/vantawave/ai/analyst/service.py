from __future__ import annotations

from pathlib import Path

from vantawave.ai.analyst.grounded import build_grounded_report
from vantawave.ai.analyst.similarity import similar_incidents
from vantawave.ai.rag.index import KnowledgeIndex


class SecurityAnalystService:
    def __init__(
        self,
        *,
        knowledge_paths: list[str | Path] | None = None,
        top_k: int = 5,
    ):
        self.knowledge_paths = [Path(path) for path in (knowledge_paths or [])]
        self.top_k = top_k
        self._index = None
        self._retriever = None

    def _ensure_index(self):
        if self._retriever is not None:
            return
        if not self.knowledge_paths:
            self._index = KnowledgeIndex(documents=[], chunks=[])
            self._retriever = None
            return

        index = KnowledgeIndex.from_paths(self.knowledge_paths)
        self._index = index
        self._retriever = index.tfidf() if index.chunks else None

    def analyze(
        self,
        *,
        incident: dict,
        historical_incidents: list[dict] | None = None,
        query: str | None = None,
    ):
        self._ensure_index()

        query = query or " ".join(
            str(incident.get(key) or "")
            for key in ("title", "severity", "predicted_class")
        )
        retrieved = (
            self._retriever.search(query, top_k=self.top_k)
            if self._retriever is not None
            else []
        )
        similar = similar_incidents(
            incident,
            historical_incidents or [],
            top_k=min(3, self.top_k),
        )
        return build_grounded_report(
            incident=incident,
            retrieved=retrieved,
            similar_incidents=similar,
        )
