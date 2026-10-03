from __future__ import annotations

import re

from vantawave.ai.rag.documents import KnowledgeChunk, KnowledgeDocument


def _split_paragraphs(text: str) -> list[tuple[int, int, str]]:
    chunks = []
    for match in re.finditer(r"\S(?:.|\n)*?(?=\n\s*\n|\Z)", text, flags=re.MULTILINE):
        raw = match.group(0).strip()
        if raw:
            chunks.append((match.start(), match.end(), raw))
    return chunks


def chunk_document(
    document: KnowledgeDocument,
    *,
    max_chars: int = 1200,
    overlap_chars: int = 160,
) -> list[KnowledgeChunk]:
    if max_chars < 200:
        raise ValueError("max_chars must be at least 200.")
    if not 0 <= overlap_chars < max_chars:
        raise ValueError("overlap_chars must be >= 0 and < max_chars.")

    paragraphs = _split_paragraphs(document.text)
    chunks: list[KnowledgeChunk] = []

    buffer = ""
    buffer_start = 0
    current_end = 0

    def emit(text: str, start: int, end: int):
        text = text.strip()
        if not text:
            return
        index = len(chunks) + 1
        chunks.append(
            KnowledgeChunk(
                chunk_id=f"{document.document_id}-{index:04d}",
                document_id=document.document_id,
                title=document.title,
                source=document.source,
                text=text,
                start_char=int(start),
                end_char=int(end),
                metadata=dict(document.metadata),
            )
        )

    for start, end, paragraph in paragraphs:
        candidate = f"{buffer}\n\n{paragraph}".strip() if buffer else paragraph
        if len(candidate) <= max_chars:
            if not buffer:
                buffer_start = start
            buffer = candidate
            current_end = end
            continue

        if buffer:
            emit(buffer, buffer_start, current_end)

        if len(paragraph) <= max_chars:
            buffer = paragraph
            buffer_start = start
            current_end = end
            continue

        step = max_chars - overlap_chars
        cursor = 0
        while cursor < len(paragraph):
            piece = paragraph[cursor:cursor + max_chars]
            emit(piece, start + cursor, min(start + cursor + len(piece), end))
            cursor += step
        buffer = ""
        current_end = end

    if buffer:
        emit(buffer, buffer_start, current_end)

    return chunks
