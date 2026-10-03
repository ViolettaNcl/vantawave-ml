from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GroundedPrompt:
    system: str
    user: str
    allowed_citations: tuple[str, ...]


def build_grounded_prompt(report_payload: dict, *, question: str) -> GroundedPrompt:
    citations = []
    evidence_lines = []

    for item in report_payload.get("evidence", []):
        citation = item["citation"]
        citations.append(citation)
        evidence_lines.append(
            f"{citation} {item['label']}: {item.get('payload', {})}"
        )

    for item in report_payload.get("retrieved_context", []):
        citation = item.get("citation")
        if not citation:
            continue
        citations.append(citation)
        chunk = item.get("chunk", {})
        evidence_lines.append(
            f"{citation} {chunk.get('title', 'Knowledge')}: {chunk.get('text', '')}"
        )

    system = (
        "You are the VantaWave Security Analyst. "
        "Answer only from the supplied evidence. "
        "Every concrete security claim must include one or more allowed citations. "
        "Do not invent packets, credentials, devices, attacks, scores, timestamps, "
        "or configuration values. If the evidence is insufficient, say so. "
        "Do not provide autonomous attack execution steps."
    )

    user = (
        f"Question: {question}\n\n"
        "Evidence:\n"
        + "\n".join(evidence_lines)
        + "\n\nReturn a concise evidence-grounded analysis with citations."
    )
    return GroundedPrompt(
        system=system,
        user=user,
        allowed_citations=tuple(dict.fromkeys(citations)),
    )
