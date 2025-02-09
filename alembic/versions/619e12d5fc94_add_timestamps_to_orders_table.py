"""add timestamps to orders table

Revision ID: 619e12d5fc94
Revises: 639f988b778e
Create Date: 2025-02-08 12:16:00.648104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision: str = '619e12d5fc94'
down_revision: Union[str, None] = '639f988b778e'
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
        sa.Column('shipping_address_id', sa.Integer, sa.ForeignKey('addresses.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False)
    )

def downgrade():
    # Drop orders table
    op.drop_table('orders')

    # Drop ENUM type for order status
    order_status_enum.drop(op.get_bind(), checkfirst=True)