"""zarpe

Revision ID: cd860b2c24bc
Revises: 635631e9eab3
Create Date: 2025-11-24 13:32:13.383778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'cd860b2c24bc'
down_revision: Union[str, Sequence[str], None] = '635631e9eab3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('zarpe',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_tour', sa.Integer(), nullable=True),
    sa.Column('id_guia', sa.Integer(), nullable=True),
    sa.Column('detalles', sa.JSON(), nullable=True),
    sa.Column('capitan', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('marinero', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('observaciones', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('id_usuario_created', sa.Uuid(), nullable=True),
    sa.Column('id_usuario_updated', sa.Uuid(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=False),
    sa.Column('updated_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['id_guia'], ['guia.id'], ),
    sa.ForeignKeyConstraint(['id_tour'], ['tour.id'], ),
    sa.ForeignKeyConstraint(['id_usuario_created'], ['user.id'], ),
    sa.ForeignKeyConstraint(['id_usuario_updated'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('zarpe')
