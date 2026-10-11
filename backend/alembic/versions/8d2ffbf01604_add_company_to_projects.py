"""add company to projects

Revision ID: 8d2ffbf01604
Revises: 3e24d0dc9ba1
Create Date: 2026-09-15 13:52:18.616084

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d2ffbf01604'
down_revision: Union[str, Sequence[str], None] = '3e24d0dc9ba1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Adiciona a coluna temporariamente permitindo NULL
    op.add_column(
        "projects",
        sa.Column(
            "company_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    # 2. Associa os projetos existentes à empresa atual
    op.execute(
        """
        UPDATE projects
        SET company_id = '6171883c-8bcc-4b6c-9f1d-0a82f4ec4337'
        WHERE company_id IS NULL
        """
    )

    # 3. Agora que todos os projetos possuem empresa,
    #    podemos tornar a coluna obrigatória
    op.alter_column(
        "projects",
        "company_id",
        existing_type=sa.UUID(),
        nullable=False,
    )

    # 4. Índice
    op.create_index(
        op.f("ix_projects_company_id"),
        "projects",
        ["company_id"],
        unique=False,
    )

    # 5. Foreign key
    op.create_foreign_key(
        "fk_projects_company_id_companies",
        "projects",
        "companies",
        ["company_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_projects_company_id_companies",
        "projects",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_projects_company_id"),
        table_name="projects",
    )

    op.drop_column(
        "projects",
        "company_id",
    )
