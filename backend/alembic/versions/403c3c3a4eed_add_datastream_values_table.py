"""add datastream_values table

Revision ID: 403c3c3a4eed
Revises: df961a351bec
Create Date: 2026-10-12 10:21:21.337002

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '403c3c3a4eed'
down_revision: Union[str, Sequence[str], None] = 'df961a351bec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # NOTE: the autogenerate run also detected the known spurious diff on
    # projects.owner_id's FK ON DELETE behavior - stripped out per
    # README_CIAO.md; only the new table/indexes are applied here.
    op.create_table('datastream_values',
    sa.Column('datastream_id', sa.UUID(), nullable=False),
    sa.Column('value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['datastream_id'], ['datastreams.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_datastream_values_datastream_id'), 'datastream_values', ['datastream_id'], unique=False)
    op.create_index('ix_datastream_values_datastream_id_recorded_at', 'datastream_values', ['datastream_id', 'recorded_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_datastream_values_datastream_id_recorded_at', table_name='datastream_values')
    op.drop_index(op.f('ix_datastream_values_datastream_id'), table_name='datastream_values')
    op.drop_table('datastream_values')
