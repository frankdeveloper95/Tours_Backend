"""Add is_active to Tour

Revision ID: f0b37d2b3940
Revises: 3744e7f89858
Create Date: 2026-01-19 15:15:31.638335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'f0b37d2b3940'
down_revision: Union[str, Sequence[str], None] = '3744e7f89858'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tour",
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False)
    )


def downgrade() -> None:
    op.drop_column("tour", "is_active")
