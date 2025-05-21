"""add navitem table

Revision ID: 4f7e8f5d8705
Revises: 
Create Date: 2025-05-21 16:35:54.192410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4f7e8f5d8705'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'navitems',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('navitems.id', ondelete='CASCADE'), nullable=True),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=255), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

def downgrade():
    op.drop_table('navitems')
