"""initial persistent monitoring schema

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "lab_targets",
        sa.Column("target_id", sa.String(32), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("ssid", sa.String(200), nullable=False),
        sa.Column("bssid", sa.String(32), nullable=False),
        sa.Column("authorized", sa.Boolean(), nullable=False),
        sa.Column("owner_confirmation", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("bssid"),
    )
    op.create_index("ix_lab_targets_bssid", "lab_targets", ["bssid"])

    op.create_table(
        "sensor_sessions",
        sa.Column("session_id", sa.String(32), primary_key=True),
        sa.Column("target_id", sa.String(32), sa.ForeignKey("lab_targets.target_id"), nullable=True),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("mode", sa.String(100), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("event_count", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_sensor_sessions_target_id", "sensor_sessions", ["target_id"])

    op.create_table(
        "incidents",
        sa.Column("incident_id", sa.String(32), primary_key=True),
        sa.Column("session_id", sa.String(32), sa.ForeignKey("sensor_sessions.session_id"), nullable=True),
        sa.Column("target_id", sa.String(32), sa.ForeignKey("lab_targets.target_id"), nullable=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("severity", sa.String(32), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("anomaly_score", sa.Float(), nullable=True),
        sa.Column("predicted_class", sa.String(100), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_incidents_session_id", "incidents", ["session_id"])
    op.create_index("ix_incidents_target_id", "incidents", ["target_id"])

    op.create_table(
        "drift_events",
        sa.Column("drift_id", sa.String(32), primary_key=True),
        sa.Column("feature", sa.String(200), nullable=False),
        sa.Column("kind", sa.String(100), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("severity", sa.String(32), nullable=False),
        sa.Column("baseline_version", sa.String(100), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_drift_events_feature", "drift_events", ["feature"])

    op.create_table(
        "model_snapshots",
        sa.Column("snapshot_id", sa.String(32), primary_key=True),
        sa.Column("model_name", sa.String(200), nullable=False),
        sa.Column("model_version", sa.String(100), nullable=False),
        sa.Column("alias", sa.String(100), nullable=True),
        sa.Column("threshold", sa.Float(), nullable=True),
        sa.Column("metrics_json", sa.JSON(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_model_snapshots_model_name", "model_snapshots", ["model_name"])

    op.create_table(
        "evaluation_runs",
        sa.Column("evaluation_id", sa.String(32), primary_key=True),
        sa.Column("model_name", sa.String(200), nullable=False),
        sa.Column("dataset_name", sa.String(200), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("metrics_json", sa.JSON(), nullable=False),
        sa.Column("recommendation", sa.String(100), nullable=True),
        sa.Column("reasons_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_evaluation_runs_model_name", "evaluation_runs", ["model_name"])


def downgrade():
    op.drop_table("evaluation_runs")
    op.drop_table("model_snapshots")
    op.drop_table("drift_events")
    op.drop_table("incidents")
    op.drop_table("sensor_sessions")
    op.drop_table("lab_targets")
