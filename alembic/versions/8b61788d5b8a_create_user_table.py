"""create_user_table

Revision ID: 8b61788d5b8a
Revises: 31617e4102b8
Create Date: 2025-01-22 15:09:43.165907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b61788d5b8a'
down_revision: Union[str, None] = '31617e4102b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
