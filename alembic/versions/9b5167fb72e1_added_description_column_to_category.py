"""Added description column to Category

Revision ID: 9b5167fb72e1
Revises: 
Create Date: 2025-01-30 15:38:48.898201

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9b5167fb72e1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('categories', sa.Column('description', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('categories', 'description')

