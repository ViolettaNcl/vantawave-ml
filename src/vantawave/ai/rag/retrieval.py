from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib.util import find_spec
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from vantawave.ai.rag.documents import KnowledgeChunk


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: KnowledgeChunk
    score: float
    rank: int

    def to_dict(self):
        return {
            "score": self.score,
            "rank": self.rank,
            "chunk": self.chunk.to_dict(),
            "citation": self.chunk.citation,
        }


class TfidfRetriever:
    def __init__(self, chunks: list[KnowledgeChunk]):
        if not chunks:
            raise ValueError("At least one knowledge chunk is required.")
        self.chunks = list(chunks)
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=1,
            stop_words=None,
        )
        self.matrix = self.vectorizer.fit_transform(chunk.text for chunk in self.chunks)

    def search(self, query: str, *, top_k: int = 5) -> list[RetrievedChunk]:
        if not query.strip():
            return []
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix)[0]
        order = np.argsort(scores)[::-1][:top_k]
        return [
            RetrievedChunk(
                chunk=self.chunks[int(index)],
                score=float(scores[int(index)]),
                rank=rank,
            )
            for rank, index in enumerate(order, start=1)
            if scores[int(index)] > 0
        ]


class SemanticRetriever:
    def __init__(
        self,
        chunks: list[KnowledgeChunk],
        *,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        if find_spec("sentence_transformers") is None:
            raise RuntimeError(
                'Sentence Transformers is optional. Install: pip install -e ".[embeddings]"'
            )
        from sentence_transformers import SentenceTransformer

        self.chunks = list(chunks)
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embeddings = self.model.encode(
            [chunk.text for chunk in chunks],
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def search(self, query: str, *, top_k: int = 5) -> list[RetrievedChunk]:
        if not query.strip():
            return []
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]
        scores = np.asarray(self.embeddings) @ np.asarray(query_embedding)
        order = np.argsort(scores)[::-1][:top_k]
        return [
            RetrievedChunk(
                chunk=self.chunks[int(index)],
                score=float(scores[int(index)]),
                rank=rank,
            )
            for rank, index in enumerate(order, start=1)
        ]
