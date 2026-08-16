"""Add partial unique index to enforce at most one active digest cycle

Revision ID: 002
Revises: 001
Create Date: 2026-08-16
"""
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Allows at most one row in digest_cycles with status 'pending' or 'running'.
    # A second concurrent INSERT with either status raises IntegrityError.
    op.execute(
        """
        CREATE UNIQUE INDEX uq_digest_cycles_active
        ON digest_cycles (status)
        WHERE status IN ('pending', 'running')
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_digest_cycles_active")
