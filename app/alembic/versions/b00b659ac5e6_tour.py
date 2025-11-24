"""tour

Revision ID: b00b659ac5e6
Revises: dfadc0013d4d
Create Date: 2025-11-20 23:47:35.921783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'b00b659ac5e6'
down_revision: Union[str, Sequence[str], None] = 'dfadc0013d4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('tour',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_operadora', sa.Integer(), nullable=True),
    sa.Column('id_guia', sa.Integer(), nullable=True),
    sa.Column('nombre', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('descripcion', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('fecha', sa.Date(), nullable=False),
    sa.Column('hora_inicio', sa.Time(), nullable=False),
    sa.Column('hora_fin', sa.Time(), nullable=False),
    sa.Column('precio', sa.Integer(), nullable=False),
    sa.Column('capacidad_maxima', sa.Integer(), nullable=False),
    sa.Column('destino', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('image_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=False),
    sa.Column('updated_date', sa.DateTime(), nullable=True),
    sa.Column('id_usuario_created', sa.Uuid(), nullable=True),
    sa.Column('id_usuario_updated', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['id_guia'], ['guia.id'], ),
    sa.ForeignKeyConstraint(['id_operadora'], ['operadora.id'], ),
    sa.ForeignKeyConstraint(['id_usuario_created'], ['user.id'], ),
    sa.ForeignKeyConstraint(['id_usuario_updated'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('tour')
