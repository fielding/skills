#!/usr/bin/env bash
# Copies this case's fixtures into the run's throwaway working directory.
# `claude plugin eval` runs this as you (not sandboxed) with cwd already set there.
#
# Then builds a small git history whose commit messages carry the session's story, so a
# retro invoked detached from the session has a real `git log` to reconstruct from.
# .handoff/ and .gate/ are gitignored and stay untracked, as they would be in a real repo.
set -euo pipefail
cp -R "$(dirname "$0")/fixtures/." .
git init -q
commit() { git -c user.email=e@x -c user.name=e commit -q -m "$1"; }

git add README.md pyproject.toml uv.lock .gitignore app/__init__.py app/main.py
commit "Bootstrap ledgerd: FastAPI skeleton, uv-managed project"

# The migration as first submitted for review: irreversible.
cat > migrations/versions/0007_accounts.py <<'PY'
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
    pass
PY
git add app/routes/accounts.py migrations/versions/0007_accounts.py
commit "Add account export endpoint and 0007_accounts migration (#212)"

git add app/deps.py
commit "fix(lint): ruff B008 on Depends() defaults; use Annotated[Session, Depends(get_db)] (#212)"

cp "$(dirname "$0")/fixtures/migrations/versions/0007_accounts.py" migrations/versions/0007_accounts.py
git add migrations/versions/0007_accounts.py
commit "migrations: real downgrade() for 0007_accounts per maya's review; rename UserRepo -> AccountRepo (#212)"
