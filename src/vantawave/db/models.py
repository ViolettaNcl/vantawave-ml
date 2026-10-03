from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from vantawave.db.base import Base, TimestampMixin


class LabTargetRecord(TimestampMixin, Base):
    __tablename__ = "lab_targets"

    target_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    ssid: Mapped[str] = mapped_column(String(200), nullable=False)
    bssid: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    authorized: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    owner_confirmation: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class SensorSessionRecord(TimestampMixin, Base):
    __tablename__ = "sensor_sessions"

    session_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    target_id: Mapped[str | None] = mapped_column(
        ForeignKey("lab_targets.target_id"),
        nullable=True,
        index=True,
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    mode: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="created")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    event_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class IncidentRecord(TimestampMixin, Base):
    __tablename__ = "incidents"

    incident_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    session_id: Mapped[str | None] = mapped_column(
        ForeignKey("sensor_sessions.session_id"),
        nullable=True,
        index=True,
    )
    target_id: Mapped[str | None] = mapped_column(
        ForeignKey("lab_targets.target_id"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    anomaly_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    predicted_class: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    evidence_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class DriftEventRecord(TimestampMixin, Base):
    __tablename__ = "drift_events"

    drift_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    feature: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    baseline_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class ModelSnapshotRecord(TimestampMixin, Base):
    __tablename__ = "model_snapshots"

    snapshot_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    model_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    alias: Mapped[str | None] = mapped_column(String(100), nullable=True)
    threshold: Mapped[float | None] = mapped_column(Float, nullable=True)
    metrics_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class EvaluationRunRecord(TimestampMixin, Base):
    __tablename__ = "evaluation_runs"

    evaluation_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    model_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
    metrics_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    recommendation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reasons_json: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
