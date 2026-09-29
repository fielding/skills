#!/usr/bin/env bash
# Copies this case's fixtures into the run's throwaway working directory.
# `claude plugin eval` runs this as you (not sandboxed) with cwd already set there.
set -euo pipefail
cp -R "$(dirname "$0")/fixtures/." .
# Repo state gate expects: a base on main, and the change under review as one loose wip
# commit on a feature branch (gate diffs base...HEAD and would early-exit on an empty diff).
git init -q -b main
git add -A
git -c user.email=e@x -c user.name=e commit -qm "shoplite: cart pricing with per-line totals"
git checkout -qb feature/bulk-discount
cp -R "$(dirname "$0")/change/." .
git add -A
git -c user.email=e@x -c user.name=e commit -qm "wip: bulk discount tiers"
# Pre-sync the dev venv (ruff, pytest) from the lockfile so the floor runs with no network.
uv sync --frozen --offline -q 2>/dev/null || uv sync --frozen -q
