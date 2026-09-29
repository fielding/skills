#!/usr/bin/env bash
# Copies this case's fixtures into the run's throwaway working directory.
# `claude plugin eval` runs this as you (not sandboxed) with cwd already set there.
#
# Builds a two-commit history for the session; .handoff/ (including the existing retro note
# from 2026-08-12) and .gate/ are gitignored and stay untracked.
set -euo pipefail
cp -R "$(dirname "$0")/fixtures/." .
git init -q
commit() { git -c user.email=e@x -c user.name=e commit -q -m "$1"; }
git add README.md pyproject.toml uv.lock .gitignore app/__init__.py app/main.py app/deps.py
commit "ledgerd: FastAPI skeleton, uv-managed project"
git add app/routes/accounts.py tests/conftest.py
commit "export endpoint: camelCase response model (priya); per-test sqlite file for xdist (#231)"
