"""create datastreams table

Revision ID: ea839d03eea6
Revises: f4ca78204707
Create Date: 2026-10-02 21:49:58.991502

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea839d03eea6'
down_revision: Union[str, Sequence[str], None] = 'f4ca78204707'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "datastreams",
        sa.Column("device_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("data_type", sa.String(length=30), nullable=False),
        sa.Column("unit", sa.String(length=30), nullable=True),
        sa.Column("min_value", sa.Float(), nullable=True),
        sa.Column("max_value", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["device_id"],
            ["devices.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_datastreams_device_id"),
        "datastreams",
        ["device_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_datastreams_key"),
        "datastreams",
        ["key"],
        unique=False,
    )

def downgrade() -> None:
    op.drop_index(
        op.f("ix_datastreams_key"),
        table_name="datastreams",
    )

    op.drop_index(
        op.f("ix_datastreams_device_id"),
        table_name="datastreams",
    )

    op.drop_table("datastreams")
