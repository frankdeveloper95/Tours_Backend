"""operadora

Revision ID: 64e289d1b242
Revises: b0cde5cb8d6f
Create Date: 2025-11-20 19:36:15.762203

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '64e289d1b242'
down_revision: Union[str, Sequence[str], None] = 'b0cde5cb8d6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('operadora',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.Column('razon_social', sqlmodel.sql.sqltypes.AutoString(length=150), nullable=False),
    sa.Column('correo', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.Column('telefono', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
    sa.Column('direccion', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.Column('created_date', sa.DateTime(), nullable=False),
    sa.Column('updated_date', sa.DateTime(), nullable=True),
    sa.Column('id_usuario_created', sa.Uuid(), nullable=True),
    sa.Column('id_usuario_updated', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['id_usuario_created'], ['user.id'], ),
    sa.ForeignKeyConstraint(['id_usuario_updated'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('correo'),
    sa.UniqueConstraint('telefono')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('operadora')
