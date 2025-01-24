"""empty message

Revision ID: 2eeded4065ef
Revises: 8b61788d5b8a
Create Date: 2025-01-23 18:09:35.656601

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2eeded4065ef'
down_revision: Union[str, None] = '8b61788d5b8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
