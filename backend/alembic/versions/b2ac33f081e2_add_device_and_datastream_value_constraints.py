"""constrain device status and datastream data types

Revision ID: b2ac33f081e2
Revises: 5b8cf21ad804
"""
from typing import Sequence, Union

from alembic import op

revision: str = "b2ac33f081e2"
down_revision: Union[str, Sequence[str], None] = "5b8cf21ad804"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_devices_status",
        "devices",
        "status IN ('online', 'offline')",
    )
    op.create_check_constraint(
        "ck_datastreams_data_type",
        "datastreams",
        "data_type IN ('boolean', 'integer', 'float', 'string', 'json')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_datastreams_data_type", "datastreams", type_="check")
    op.drop_constraint("ck_devices_status", "devices", type_="check")
