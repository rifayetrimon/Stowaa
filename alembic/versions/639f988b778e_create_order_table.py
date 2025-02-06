"""create order table

Revision ID: 639f988b778e
Revises: 00ce2dcb5784
Create Date: 2025-02-05 12:15:29.674793

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision: str = '639f988b778e'
down_revision: Union[str, None] = '00ce2dcb5784'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


order_status_enum = ENUM('PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED', name='orderstatus', create_type=False)

def upgrade():
    # Create ENUM type for order status if not exists
    order_status_enum.create(op.get_bind(), checkfirst=True)

    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', order_status_enum, nullable=False, server_default='PENDING'),
        sa.Column('total_amount', sa.Float, nullable=False),
        sa.Column('shipping_address_id', sa.Integer, sa.ForeignKey('addresses.id'), nullable=True)
    )

def downgrade():
    # Drop orders table
    op.drop_table('orders')

    # Drop ENUM type for order status
    order_status_enum.drop(op.get_bind(), checkfirst=True)
