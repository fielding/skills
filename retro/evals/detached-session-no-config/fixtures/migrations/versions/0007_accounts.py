"""accounts: add exported_at

Revision ID: 0007
Revises: 0006
"""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"


def upgrade() -> None:
    op.add_column("accounts", sa.Column("exported_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_accounts_exported_at", "accounts", ["exported_at"])


def downgrade() -> None:
    op.drop_index("ix_accounts_exported_at", table_name="accounts")
    op.drop_column("accounts", "exported_at")
