"""merge heads

Revision ID: cc8f364d5c43
Revises: c35a37ceea72, cd860b2c24bc
Create Date: 2026-01-18 22:38:19.381171

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'cc8f364d5c43'
down_revision: Union[str, Sequence[str], None] = ('c35a37ceea72', 'cd860b2c24bc')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
