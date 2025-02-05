"""Add created_at and updated_at to wishlist table

Revision ID: 00ce2dcb5784
Revises: ace62678be4f
Create Date: 2025-02-05 10:45:09.582477

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '00ce2dcb5784'
down_revision: Union[str, None] = 'ace62678be4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add the columns
    op.add_column('wishlist', sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()))
    op.add_column('wishlist', sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()))

def downgrade():
    # Remove the columns in case of rollback
    op.drop_column('wishlist', 'created_at')
    op.drop_column('wishlist', 'updated_at')