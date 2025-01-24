"""Add products and categories tables

Revision ID: e95c0e7b743d
Revises: 2eeded4065ef
Create Date: 2025-01-23 18:23:09.150932

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e95c0e7b743d'
down_revision: Union[str, None] = '2eeded4065ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # Create 'categories' table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True)
    )

    # Create 'products' table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('stock_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('categories.id'), nullable=False),
        sa.Column('image_url', sa.String(length=512), nullable=True)
    )


def downgrade() -> None:
    # Drop 'products' table
    op.drop_table('products')

    # Drop 'categories' table
    op.drop_table('categories')
