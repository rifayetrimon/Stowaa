"""crate enum and banner table

Revision ID: 8f50a092b82c
Revises:
Create Date: 2025-05-22 15:16:19.381194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8f50a092b82c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "banners",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("image_url", sa.String(255), nullable=False),
        sa.Column(
            "banner_type",
            sa.Enum(
                "default", "regular",
                name="bannertype",
                create_type=True,  # Creates the ENUM type in PostgreSQL
            ),
            nullable=False,
            server_default="regular"
        ),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )


def downgrade():
    op.drop_table("banners")
    op.execute("DROP TYPE IF EXISTS bannertype;")