"""Remove updated_at from wishlist

Revision ID: ace62678be4f
Revises: d4d328258443
Create Date: 2025-02-05 10:14:46.264741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ace62678be4f'
down_revision: Union[str, None] = 'd4d328258443'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Either drop the constraint first:
    op.drop_constraint('order_items_order_id_fkey', 'order_items', type_='foreignkey')
    op.drop_table('orders')
    
    # Or use CASCADE (alternative approach):
    # op.execute('DROP TABLE orders CASCADE')
