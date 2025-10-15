from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_accounting"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "account",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )

    op.create_table(
        "journalentry",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("reference", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("posted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("posted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "journalline",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("journal_entry_id", sa.Integer(), sa.ForeignKey("journalentry.id"), nullable=False),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("account.id"), nullable=False),
        sa.Column("debit", sa.Float(), nullable=False, server_default="0"),
        sa.Column("credit", sa.Float(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("journalline")
    op.drop_table("journalentry")
    op.drop_table("account")
