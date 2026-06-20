"""Initial schema creation

Revision ID: 0001
Revises:
Create Date: 2026-06-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="analyst"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "datasets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("file_size", sa.Integer, nullable=False, server_default="0"),
        sa.Column("file_hash", sa.String(64), nullable=True),
        sa.Column("row_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(50), nullable=False, server_default="uploaded"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "accounts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("dataset_id", sa.String(36), nullable=False),
        sa.Column("external_account_ref", sa.String(255), nullable=False),
        sa.Column("masked_account_ref", sa.String(255), nullable=False),
        sa.Column("country", sa.String(10), nullable=True),
        sa.Column("account_age_days", sa.Integer, nullable=False, server_default="365"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("dataset_id", sa.String(36), nullable=False),
        sa.Column("external_transaction_ref", sa.String(255), nullable=False),
        sa.Column("timestamp", sa.DateTime, nullable=False),
        sa.Column("sender_account_id", sa.String(36), nullable=False),
        sa.Column("receiver_account_id", sa.String(36), nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("currency", sa.String(10), nullable=False, server_default="USD"),
        sa.Column("channel", sa.String(50), nullable=False, server_default="online"),
        sa.Column("sender_country", sa.String(10), nullable=True),
        sa.Column("receiver_country", sa.String(10), nullable=True),
        sa.Column("device_hash", sa.String(255), nullable=True),
        sa.Column("ip_hash", sa.String(255), nullable=True),
        sa.Column("scenario", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "analysis_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("dataset_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("metrics_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "detection_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("dataset_id", sa.String(36), nullable=False),
        sa.Column("analysis_run_id", sa.String(36), nullable=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("risk_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("reason_codes_json", sa.Text, nullable=True),
        sa.Column("evidence_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "investigation_cases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_number", sa.String(50), unique=True, nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("severity", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("primary_account_id", sa.String(36), nullable=True),
        sa.Column("risk_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.Column("assigned_to", sa.String(36), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "case_evidence",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_id", sa.String(36), nullable=False),
        sa.Column("event_id", sa.String(36), nullable=True),
        sa.Column("evidence_type", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "case_notes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("case_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "account_risk_assessments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("account_id", sa.String(36), nullable=False),
        sa.Column("analysis_run_id", sa.String(36), nullable=True),
        sa.Column("risk_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("risk_level", sa.String(20), nullable=False, server_default="LOW"),
        sa.Column("component_scores_json", sa.Text, nullable=True),
        sa.Column("reason_codes_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "graph_metrics",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("account_id", sa.String(36), nullable=False),
        sa.Column("analysis_run_id", sa.String(36), nullable=True),
        sa.Column("betweenness_centrality", sa.Float, nullable=False, server_default="0"),
        sa.Column("in_degree", sa.Integer, nullable=False, server_default="0"),
        sa.Column("out_degree", sa.Integer, nullable=False, server_default="0"),
        sa.Column("in_total_value", sa.Float, nullable=False, server_default="0"),
        sa.Column("out_total_value", sa.Float, nullable=False, server_default="0"),
        sa.Column("in_unique_counterparties", sa.Integer, nullable=False, server_default="0"),
        sa.Column("out_unique_counterparties", sa.Integer, nullable=False, server_default="0"),
        sa.Column("in_cycle", sa.String(10), nullable=False, server_default="false"),
        sa.Column("cycle_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("entity_id", sa.String(36), nullable=True),
        sa.Column("metadata_json", sa.Text, nullable=True),
        sa.Column("ip_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("graph_metrics")
    op.drop_table("account_risk_assessments")
    op.drop_table("case_notes")
    op.drop_table("case_evidence")
    op.drop_table("investigation_cases")
    op.drop_table("detection_events")
    op.drop_table("analysis_runs")
    op.drop_table("transactions")
    op.drop_table("accounts")
    op.drop_table("datasets")
    op.drop_table("users")
