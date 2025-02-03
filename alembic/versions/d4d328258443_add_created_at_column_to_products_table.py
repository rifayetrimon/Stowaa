"""Add created_at column to products table

Revision ID: d4d328258443
Revises: 5fd77afd6987
Create Date: 2025-02-01 17:24:50.742462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4d328258443'
down_revision: Union[str, None] = '5fd77afd6987'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Add the created_at column
    op.add_column('products', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()))

def downgrade():
    # Drop the created_at column
    op.drop_column('products', 'created_at')
