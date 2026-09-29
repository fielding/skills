#!/usr/bin/env bash
# Copies this case's fixtures into the run's throwaway working directory.
# `claude plugin eval` runs this as you (not sandboxed) with cwd already set there.
set -euo pipefail
cp -R "$(dirname "$0")/fixtures/." .
# One "Initial commit" dump, the shape of a vibe-coded hand-off (u07 reads git log).
git init -q -b main
git add -A
git -c user.email=e@x -c user.name=e commit -qm "Initial commit"
