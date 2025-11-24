"""guia

Revision ID: dfadc0013d4d
Revises: 64e289d1b242
Create Date: 2025-11-20 19:38:30.551769

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'dfadc0013d4d'
down_revision: Union[str, Sequence[str], None] = '64e289d1b242'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('guia',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_usuario', sa.Uuid(), nullable=True),
    sa.Column('id_operadora', sa.Integer(), nullable=True),
    sa.Column('calificacion', sa.Float(), nullable=True),
    sa.Column('idiomas', sa.JSON(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=False),
    sa.Column('updated_date', sa.DateTime(), nullable=True),
    sa.Column('id_usuario_created', sa.Uuid(), nullable=True),
    sa.Column('id_usuario_updated', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['id_operadora'], ['operadora.id'], ),
    sa.ForeignKeyConstraint(['id_usuario'], ['user.id'], ),
    sa.ForeignKeyConstraint(['id_usuario_created'], ['user.id'], ),
    sa.ForeignKeyConstraint(['id_usuario_updated'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id_usuario')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('guia')
