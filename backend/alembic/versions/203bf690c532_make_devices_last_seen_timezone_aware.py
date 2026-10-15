"""make devices.last_seen timezone-aware

Revision ID: 203bf690c532
Revises: 403c3c3a4eed
Create Date: 2026-10-15 10:13:47.942293

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '203bf690c532'
down_revision: Union[str, Sequence[str], None] = '403c3c3a4eed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # NOTE: the autogenerate run also detected the known spurious diff on
    # projects.owner_id's FK ON DELETE behavior - stripped out per
    # README_CIAO.md; only the last_seen type change is applied here.
    op.alter_column('devices', 'last_seen',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('devices', 'last_seen',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
