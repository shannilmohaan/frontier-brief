"""Add thumbnail_url column to source_items

Revision ID: 003
Revises: 002
Create Date: 2026-08-16
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("source_items", sa.Column("thumbnail_url", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("source_items", "thumbnail_url")
