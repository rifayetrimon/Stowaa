"""Fixed self-referential relationship in Category model with timestamps

Revision ID: d328e8c14999
Revises: 9b5167fb72e1
Create Date: 2025-01-30 15:49:54.332385

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd328e8c14999'
down_revision: Union[str, None] = '9b5167fb72e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('categories', sa.Column('parent_id', sa.Integer(), sa.ForeignKey('categories.id', ondelete="SET NULL"), nullable=True))

def downgrade():
    op.drop_column('categories', 'parent_id')

