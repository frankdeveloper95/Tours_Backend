"""reserva

Revision ID: 635631e9eab3
Revises: b00b659ac5e6
Create Date: 2025-11-20 23:50:37.242739

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '635631e9eab3'
down_revision: Union[str, Sequence[str], None] = 'b00b659ac5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('estado_reserva',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('estado', sa.Enum('PAGADA', 'PENDIENTE', name='reservaenum'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reservas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_tour', sa.Integer(), nullable=True),
    sa.Column('id_usuario', sa.Uuid(), nullable=True),
    sa.Column('id_reserva_estado', sa.Integer(), nullable=False),
    sa.Column('nombre_cliente', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('email_cliente', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('numero_personas', sa.Integer(), nullable=False),
    sa.Column('fecha_reserva', sa.DateTime(), nullable=True),
    sa.Column('fecha_modificacion_reserva', sa.DateTime(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=False),
    sa.Column('updated_date', sa.DateTime(), nullable=True),
    sa.Column('id_usuario_created', sa.Uuid(), nullable=True),
    sa.Column('id_usuario_updated', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['id_reserva_estado'], ['estado_reserva.id'], ),
    sa.ForeignKeyConstraint(['id_tour'], ['tour.id'], ),
    sa.ForeignKeyConstraint(['id_usuario'], ['user.id'], ),
    sa.ForeignKeyConstraint(['id_usuario_created'], ['user.id'], ),
    sa.ForeignKeyConstraint(['id_usuario_updated'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('estado_reserva')
    op.drop_table('reservas')
