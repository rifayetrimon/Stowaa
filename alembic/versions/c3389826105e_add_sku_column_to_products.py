"""add_sku_column_to_products

Revision ID: c3389826105e
Revises: 1bf43316c293
Create Date: 2025-01-31 11:24:01.774306

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3389826105e'
down_revision: Union[str, None] = '1bf43316c293'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    op.add_column('products', sa.Column('sku', sa.String(50), nullable=True)) 

def downgrade():
    op.drop_column('products', 'sku')
