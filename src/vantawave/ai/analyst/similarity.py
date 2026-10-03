from __future__ import annotations

import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _incident_text(incident: dict) -> str:
    parts = [
        str(incident.get("title") or ""),
        str(incident.get("severity") or ""),
        str(incident.get("predicted_class") or ""),
        json.dumps(incident.get("evidence_json") or incident.get("evidence") or {}, sort_keys=True),
    ]
    return " ".join(parts)


def similar_incidents(
    target: dict,
    candidates: list[dict],
    *,
    top_k: int = 5,
) -> list[dict]:
    usable = [
        item for item in candidates
        if item.get("incident_id") != target.get("incident_id")
    ]
    if not usable:
        return []

    corpus = [_incident_text(target)] + [_incident_text(item) for item in usable]
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(corpus)
    scores = cosine_similarity(matrix[0:1], matrix[1:])[0]
    order = scores.argsort()[::-1][:top_k]

    result = []
    for index in order:
        if scores[index] <= 0:
            continue
        payload = dict(usable[int(index)])
        payload["similarity_score"] = float(scores[int(index)])
        result.append(payload)
    return result
