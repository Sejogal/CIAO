"""create devices table

Revision ID: f4ca78204707
Revises: 8d2ffbf01604
Create Date: 2026-09-29 11:15:42.006584

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f4ca78204707"
down_revision: Union[str, Sequence[str], None] = "8d2ffbf01604"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "devices",
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("uuid", sa.String(length=100), nullable=False),
        sa.Column("serial", sa.String(length=100), nullable=True),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("mqtt_username", sa.String(length=100), nullable=True),
        sa.Column("mqtt_password", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("firmware_version", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("last_seen", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mqtt_username"),
        sa.UniqueConstraint("token"),
    )

    op.create_index(
        op.f("ix_devices_project_id"),
        "devices",
        ["project_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_devices_serial"),
        "devices",
        ["serial"],
        unique=True,
    )

    op.create_index(
        op.f("ix_devices_uuid"),
        "devices",
        ["uuid"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_devices_uuid"),
        table_name="devices",
    )

    op.drop_index(
        op.f("ix_devices_serial"),
        table_name="devices",
    )

    op.drop_index(
        op.f("ix_devices_project_id"),
        table_name="devices",
    )

    op.drop_table("devices")