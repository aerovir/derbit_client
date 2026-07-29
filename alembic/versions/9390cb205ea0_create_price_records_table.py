"""create price_records table

Revision ID: 9390cb205ea0
Revises:
Create Date: 2026-07-29 12:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "9390cb205ea0"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "price_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticker", sa.String(length=20), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_price_records_ticker"), "price_records", ["ticker"])
    op.create_index(op.f("ix_price_records_timestamp"), "price_records", ["timestamp"])


def downgrade() -> None:
    op.drop_index(op.f("ix_price_records_timestamp"), table_name="price_records")
    op.drop_index(op.f("ix_price_records_ticker"), table_name="price_records")
    op.drop_table("price_records")
