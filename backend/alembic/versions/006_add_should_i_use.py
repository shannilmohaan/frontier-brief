"""Add should_i_use column to digest_items

Revision ID: 006
Revises: 005
Create Date: 2026-08-16
"""
from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("digest_items", sa.Column("should_i_use", sa.String(20), nullable=True))


def downgrade() -> None:
    op.drop_column("digest_items", "should_i_use")
