"""add automation device commands and MQTT outbox

Revision ID: 5b8cf21ad804
Revises: 9d31c640a72b
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "5b8cf21ad804"
down_revision: Union[str, Sequence[str], None] = "9d31c640a72b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "automation_rules",
        sa.Column("action_type", sa.String(length=30), server_default="notification", nullable=False),
    )
    op.add_column(
        "automation_rules",
        sa.Column("target_datastream_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "automation_rules",
        sa.Column("action_value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.create_index("ix_automation_rules_target_datastream_id", "automation_rules", ["target_datastream_id"])
    op.create_foreign_key(
        "fk_automation_rules_target_datastream_id_datastreams",
        "automation_rules", "datastreams", ["target_datastream_id"], ["id"], ondelete="CASCADE",
    )

    op.create_table(
        "device_commands",
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("automation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("datastream_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["automation_id"], ["automation_rules.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["datastream_id"], ["datastreams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_device_commands_project_id", "device_commands", ["project_id"])
    op.create_index("ix_device_commands_automation_id", "device_commands", ["automation_id"])
    op.create_index("ix_device_commands_datastream_id", "device_commands", ["datastream_id"])
    op.create_index("ix_device_commands_status", "device_commands", ["status"])
    op.create_index("ix_device_commands_next_attempt_at", "device_commands", ["next_attempt_at"])


def downgrade() -> None:
    op.drop_index("ix_device_commands_next_attempt_at", table_name="device_commands")
    op.drop_index("ix_device_commands_status", table_name="device_commands")
    op.drop_index("ix_device_commands_datastream_id", table_name="device_commands")
    op.drop_index("ix_device_commands_automation_id", table_name="device_commands")
    op.drop_index("ix_device_commands_project_id", table_name="device_commands")
    op.drop_table("device_commands")
    op.drop_constraint(
        "fk_automation_rules_target_datastream_id_datastreams",
        "automation_rules", type_="foreignkey",
    )
    op.drop_index("ix_automation_rules_target_datastream_id", table_name="automation_rules")
    op.drop_column("automation_rules", "action_value")
    op.drop_column("automation_rules", "target_datastream_id")
    op.drop_column("automation_rules", "action_type")
