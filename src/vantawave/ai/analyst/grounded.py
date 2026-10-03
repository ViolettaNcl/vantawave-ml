from __future__ import annotations

from typing import Iterable

from vantawave.ai.analyst.schemas import (
    AnalystFinding,
    AnalystReport,
    EvidenceRef,
)
from vantawave.ai.rag.retrieval import RetrievedChunk


ALLOWED_SEVERITIES = {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}


def _incident_evidence(incident: dict) -> list[EvidenceRef]:
    incident_id = str(incident.get("incident_id") or "unknown")
    refs = [
        EvidenceRef(
            source_type="incident",
            source_id=incident_id,
            label="Incident record",
            payload={
                key: incident.get(key)
                for key in (
                    "title",
                    "severity",
                    "risk_score",
                    "anomaly_score",
                    "predicted_class",
                    "confidence",
                    "created_at",
                )
                if incident.get(key) is not None
            },
        )
    ]

    evidence = incident.get("evidence_json") or incident.get("evidence") or {}
    if evidence:
        refs.append(
            EvidenceRef(
                source_type="evidence",
                source_id=incident_id,
                label="Incident evidence",
                payload=dict(evidence),
            )
        )
    return refs


def build_grounded_report(
    *,
    incident: dict,
    retrieved: Iterable[RetrievedChunk] = (),
    similar_incidents: list[dict] | None = None,
) -> AnalystReport:
    incident_id = str(incident.get("incident_id") or "unknown")
    severity = str(incident.get("severity") or "INFO").upper()
    if severity not in ALLOWED_SEVERITIES:
        severity = "INFO"

    evidence_refs = _incident_evidence(incident)
    incident_cite = evidence_refs[0].citation

    findings = []
    risk_score = incident.get("risk_score")
    anomaly_score = incident.get("anomaly_score")
    predicted_class = incident.get("predicted_class")
    confidence = incident.get("confidence")

    if risk_score is not None:
        findings.append(
            AnalystFinding(
                title="Recorded risk",
                statement=f"The persisted incident risk score is {int(risk_score)}/100.",
                severity=severity,
                citations=[incident_cite],
            )
        )

    if anomaly_score is not None:
        findings.append(
            AnalystFinding(
                title="Anomaly evidence",
                statement=f"The recorded anomaly score is {float(anomaly_score):.4f}.",
                severity=severity,
                citations=[incident_cite],
            )
        )

    if predicted_class:
        class_statement = f"The classifier recorded `{predicted_class}`"
        if confidence is not None:
            class_statement += f" with confidence {float(confidence):.4f}"
        class_statement += "."
        findings.append(
            AnalystFinding(
                title="Classifier output",
                statement=class_statement,
                severity=severity,
                citations=[incident_cite],
            )
        )

    retrieved_payload = []
    for item in retrieved:
        retrieved_payload.append(item.to_dict())

    similar_incidents = similar_incidents or []
    if similar_incidents:
        ids = [str(item.get("incident_id", "unknown")) for item in similar_incidents[:3]]
        for item in similar_incidents[:3]:
            related_id = str(item.get("incident_id", "unknown"))
            evidence_refs.append(
                EvidenceRef(
                    source_type="incident",
                    source_id=related_id,
                    label="Historical incident",
                    payload={
                        key: item.get(key)
                        for key in (
                            "title",
                            "severity",
                            "risk_score",
                            "predicted_class",
                            "confidence",
                            "created_at",
                            "similarity_score",
                        )
                        if item.get(key) is not None
                    },
                )
            )
        findings.append(
            AnalystFinding(
                title="Historical similarity",
                statement=(
                    "Persisted history contains related incidents: "
                    + ", ".join(f"`{value}`" for value in ids)
                    + "."
                ),
                severity="INFO",
                citations=[f"[incident:{value}]" for value in ids],
            )
        )

    title = incident.get("title") or "Security incident"
    summary = (
        f"{title}. Severity is {severity}. "
        "This report only restates persisted evidence and retrieved project knowledge."
    )

    actions = [
        "Review the cited incident evidence before changing network configuration.",
        "Compare the current telemetry window with the stored normal baseline.",
        "Confirm whether the observed BSSID, channel, and security settings match the authorized lab target.",
    ]
    if severity in {"HIGH", "CRITICAL"}:
        actions.append(
            "Preserve relevant telemetry/evidence artifacts and investigate the authorized lab target promptly."
        )

    limitations = [
        "The analyst does not infer passwords, packet contents, or attack steps that are absent from evidence.",
        "Retrieved documentation provides context but does not override measured incident data.",
        "A high anomaly or risk score is not by itself proof of compromise.",
    ]

    return AnalystReport(
        incident_id=incident_id,
        summary=summary,
        findings=findings,
        defensive_actions=actions,
        retrieved_context=retrieved_payload,
        evidence=evidence_refs,
        limitations=limitations,
    )
