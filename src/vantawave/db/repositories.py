from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import select

from vantawave.db.models import (
    DriftEventRecord,
    EvaluationRunRecord,
    IncidentRecord,
    LabTargetRecord,
    ModelSnapshotRecord,
    SensorSessionRecord,
)


class TargetRepository:
    def __init__(self, session):
        self.session = session

    def upsert(self, payload: dict) -> LabTargetRecord:
        record = self.session.get(LabTargetRecord, payload["target_id"])
        if record is None:
            record = LabTargetRecord(target_id=payload["target_id"])
            self.session.add(record)

        record.name = payload["name"]
        record.ssid = payload["ssid"]
        record.bssid = payload["bssid"].lower()
        record.authorized = bool(payload["authorized"])
        record.owner_confirmation = payload["owner_confirmation"]
        record.notes = payload.get("notes")
        self.session.flush()
        return record

    def list(self) -> list[LabTargetRecord]:
        return list(self.session.scalars(select(LabTargetRecord).order_by(LabTargetRecord.created_at)))

    def get(self, target_id: str) -> LabTargetRecord | None:
        return self.session.get(LabTargetRecord, target_id)


class SensorSessionRepository:
    def __init__(self, session):
        self.session = session

    def upsert(self, payload: dict) -> SensorSessionRecord:
        record = self.session.get(SensorSessionRecord, payload["session_id"])
        if record is None:
            record = SensorSessionRecord(session_id=payload["session_id"])
            self.session.add(record)

        record.target_id = payload.get("target_id")
        record.source = payload.get("source") or payload.get("sensor_source") or "unknown"
        record.mode = payload.get("mode", "unknown")
        record.status = payload.get("status", "created")
        record.event_count = int(payload.get("event_count", 0))
        record.metadata_json = dict(payload.get("metadata") or {})

        for field in ("started_at", "ended_at"):
            value = payload.get(field)
            if isinstance(value, str):
                value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            setattr(record, field, value)

        self.session.flush()
        return record

    def list(self) -> list[SensorSessionRecord]:
        return list(
            self.session.scalars(
                select(SensorSessionRecord).order_by(SensorSessionRecord.created_at.desc())
            )
        )


class IncidentRepository:
    def __init__(self, session):
        self.session = session

    def add(
        self,
        *,
        incident_id: str,
        title: str,
        severity: str,
        risk_score: int,
        session_id: str | None = None,
        target_id: str | None = None,
        anomaly_score: float | None = None,
        predicted_class: str | None = None,
        confidence: float | None = None,
        evidence: dict | None = None,
    ) -> IncidentRecord:
        record = IncidentRecord(
            incident_id=incident_id,
            title=title,
            severity=severity,
            risk_score=int(risk_score),
            session_id=session_id,
            target_id=target_id,
            anomaly_score=anomaly_score,
            predicted_class=predicted_class,
            confidence=confidence,
            evidence_json=dict(evidence or {}),
        )
        self.session.add(record)
        self.session.flush()
        return record

    def list(self, *, severity: str | None = None) -> list[IncidentRecord]:
        statement = select(IncidentRecord)
        if severity:
            statement = statement.where(IncidentRecord.severity == severity)
        statement = statement.order_by(IncidentRecord.created_at.desc())
        return list(self.session.scalars(statement))


class DriftRepository:
    def __init__(self, session):
        self.session = session

    def add(
        self,
        *,
        feature: str,
        kind: str,
        score: float,
        severity: str,
        baseline_version: str | None = None,
        metadata: dict | None = None,
        drift_id: str | None = None,
    ) -> DriftEventRecord:
        record = DriftEventRecord(
            drift_id=drift_id or uuid.uuid4().hex[:12],
            feature=feature,
            kind=kind,
            score=float(score),
            severity=severity,
            baseline_version=baseline_version,
            metadata_json=dict(metadata or {}),
        )
        self.session.add(record)
        self.session.flush()
        return record

    def list(self, *, severity: str | None = None) -> list[DriftEventRecord]:
        statement = select(DriftEventRecord)
        if severity:
            statement = statement.where(DriftEventRecord.severity == severity)
        statement = statement.order_by(DriftEventRecord.created_at.desc())
        return list(self.session.scalars(statement))


class ModelSnapshotRepository:
    def __init__(self, session):
        self.session = session

    def add(
        self,
        *,
        model_name: str,
        model_version: str,
        metrics: dict,
        alias: str | None = None,
        threshold: float | None = None,
        metadata: dict | None = None,
        snapshot_id: str | None = None,
    ) -> ModelSnapshotRecord:
        record = ModelSnapshotRecord(
            snapshot_id=snapshot_id or uuid.uuid4().hex[:12],
            model_name=model_name,
            model_version=str(model_version),
            alias=alias,
            threshold=threshold,
            metrics_json=dict(metrics),
            metadata_json=dict(metadata or {}),
        )
        self.session.add(record)
        self.session.flush()
        return record

    def list(self, model_name: str | None = None) -> list[ModelSnapshotRecord]:
        statement = select(ModelSnapshotRecord)
        if model_name:
            statement = statement.where(ModelSnapshotRecord.model_name == model_name)
        statement = statement.order_by(ModelSnapshotRecord.created_at.desc())
        return list(self.session.scalars(statement))


class EvaluationRepository:
    def __init__(self, session):
        self.session = session

    def add(
        self,
        *,
        model_name: str,
        dataset_name: str,
        metrics: dict,
        recommendation: str | None,
        reasons: list[str],
        status: str = "completed",
        evaluation_id: str | None = None,
    ) -> EvaluationRunRecord:
        record = EvaluationRunRecord(
            evaluation_id=evaluation_id or uuid.uuid4().hex[:12],
            model_name=model_name,
            dataset_name=dataset_name,
            metrics_json=dict(metrics),
            recommendation=recommendation,
            reasons_json=list(reasons),
            status=status,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def list(self) -> list[EvaluationRunRecord]:
        return list(
            self.session.scalars(
                select(EvaluationRunRecord).order_by(EvaluationRunRecord.created_at.desc())
            )
        )
