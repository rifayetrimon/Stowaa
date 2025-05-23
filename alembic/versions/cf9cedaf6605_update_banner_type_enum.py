"""update_banner_type_enum

Revision ID: cf9cedaf6605
Revises: 
Create Date: 2025-05-23 10:22:47.549364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'cf9cedaf6605'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Create enum type first (PostgreSQL specific)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'bannertype') THEN
            CREATE TYPE bannertype AS ENUM ('default', 'regular');
        END IF;
    END$$;
    """)

    # Create table with enum column
    op.create_table('banners',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('image_url', sa.String(length=255), nullable=False),
        sa.Column('banner_type', postgresql.ENUM('default', 'regular', name='bannertype',
                          create_type=False),
                 nullable=False, server_default='regular'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(),
                onupdate=sa.func.now())
    )

def downgrade():
    # Drop table first
    op.drop_table('banners')

    # Drop enum type
    op.execute("DROP TYPE IF EXISTS bannertype")
    # Drop table first
    op.drop_table('banners')

    # Force-drop ENUM
    op.execute("DROP TYPE IF EXISTS bannertype")
    # Drop table first
    op.drop_table('banners')

    # Drop ENUM only if not used elsewhere
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_catalog.pg_type
            JOIN pg_catalog.pg_enum ON pg_enum.enumtypid = pg_type.oid
            WHERE pg_type.typname = 'bannertype'
        ) THEN
            DROP TYPE bannertype;
        END IF;
    END$$;
    """)
    # Drop the 'banners' table
    op.drop_table('banners')

    # Drop the ENUM type (for PostgreSQL)
    banner_type_enum = postgresql.ENUM(name='bannertype')
    banner_type_enum.drop(op.get_bind())
    # ### For PostgreSQL - Restore previous enum ###
    op.execute("ALTER TYPE bannertype RENAME TO bannertype_temp")
    sa.Enum('regular', 'promotional', name='bannertype').create(op.get_bind())  # Assuming previous values

    op.alter_column('banners', 'banner_type',
                   type_=sa.Enum('regular', 'promotional', name='bannertype'),
                   postgresql_using='banner_type::text::bannertype',
                   nullable=False)

    op.execute("DROP TYPE bannertype_temp")