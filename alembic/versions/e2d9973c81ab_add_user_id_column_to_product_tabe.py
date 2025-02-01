"""add user_id column to product tabe

Revision ID: e2d9973c81ab
Revises: c3389826105e
Create Date: 2025-02-01 12:15:54.189543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e2d9973c81ab'
down_revision: Union[str, None] = 'c3389826105e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), index=True),
        sa.Column('description', sa.Text()),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('stock_quantity', sa.Integer(), server_default='0'),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('categories.id')),
        sa.Column('sku', sa.String(length=50), unique=True),
        sa.Column('image_url', sa.String(length=255)),
        sa.Column('is_active', sa.Boolean(), server_default=sa.true()),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'))
    )

def downgrade():
    op.drop_table('products')
