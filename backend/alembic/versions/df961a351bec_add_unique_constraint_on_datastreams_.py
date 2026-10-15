"""add unique constraint on datastreams device_id key

Revision ID: df961a351bec
Revises: ea839d03eea6
Create Date: 2026-10-12 09:50:37.223947

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df961a351bec'
down_revision: Union[str, Sequence[str], None] = 'ea839d03eea6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # NOTE: the autogenerate run also detected a spurious diff on
    # projects.owner_id's FK ON DELETE behavior (model says RESTRICT, DB
    # has CASCADE) - intentionally stripped out per README_CIAO.md known
    # gotcha; only the unique constraint is applied here.
    op.create_unique_constraint('uq_datastreams_device_id_key', 'datastreams', ['device_id', 'key'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_datastreams_device_id_key', 'datastreams', type_='unique')
