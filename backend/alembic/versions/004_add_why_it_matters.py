"""Add why_it_matters and importance columns to digest_items

Revision ID: 004
Revises: 003
Create Date: 2026-08-16
"""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("digest_items", sa.Column("why_it_matters", sa.Text(), nullable=True))
    op.add_column("digest_items", sa.Column("importance", sa.Integer(), nullable=False, server_default="3"))


def downgrade() -> None:
    op.drop_column("digest_items", "importance")
    op.drop_column("digest_items", "why_it_matters")
