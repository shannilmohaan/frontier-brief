"""Add builder intelligence fields to digest_items

Revision ID: 005
Revises: 004
Create Date: 2026-08-16
"""
from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("digest_items", sa.Column("what_changed", sa.Text(), nullable=True))
    op.add_column("digest_items", sa.Column("who_should_care", sa.Text(), nullable=True))
    op.add_column("digest_items", sa.Column("build_impact", sa.String(20), nullable=True))
    op.add_column("digest_items", sa.Column("production_readiness", sa.String(30), nullable=True))


def downgrade() -> None:
    op.drop_column("digest_items", "production_readiness")
    op.drop_column("digest_items", "build_impact")
    op.drop_column("digest_items", "who_should_care")
    op.drop_column("digest_items", "what_changed")
