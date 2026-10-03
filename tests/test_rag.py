from vantawave.ai.rag.index import KnowledgeIndex


def test_tfidf_retrieval_returns_relevant_chunk(tmp_path):
    doc = tmp_path / "wifi.md"
    doc.write_text(
        "# Wi-Fi defensive guide\n\n"
        "Repeated deauthentication events can be investigated by checking "
        "management-frame telemetry and the authorized AP configuration.\n\n"
        "Database migrations are unrelated to wireless management frames.",
        encoding="utf-8",
    )

    index = KnowledgeIndex.from_paths([doc])
    assert len(index.documents) == 1
    assert len(index.chunks) >= 1

    results = index.tfidf().search(
        "deauthentication management frame investigation",
        top_k=3,
    )
    assert results
    assert "deauthentication" in results[0].chunk.text.lower()
    assert results[0].chunk.citation.startswith("[")
