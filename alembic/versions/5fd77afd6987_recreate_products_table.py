"""Recreate products table

Revision ID: 5fd77afd6987
Revises: 
Create Date: 2025-02-01 17:12:43.599162
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '5fd77afd6987'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Check if the 'products' table exists before attempting to drop it
    bind = op.get_bind()
    inspector = inspect(bind)
    if 'products' in inspector.get_table_names():
        op.drop_table('products')

    # Recreate the table with created_at column
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=255), index=True),
        sa.Column('description', sa.Text()),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('stock_quantity', sa.Integer(), default=0),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey("categories.id")),
        sa.Column('sku', sa.String(length=50), unique=True),
        sa.Column('image_url', sa.String(length=255)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now())  # Added created_at column
    )

def downgrade():
    op.drop_table('products')
