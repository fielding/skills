#!/usr/bin/env bash
# Builds this case's git repo in the run's throwaway working directory: the base tree is
# committed on master, then the change is overlaid UNCOMMITTED on a feature branch.
# `claude plugin eval` runs this as you (not sandboxed) with cwd already set there.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
cp -R "$here/fixtures/repo/." .
git init -q --template= -b master
git add -A
git -c user.email=e@x -c user.name=e -c commit.gpgsign=false -c core.hooksPath=/dev/null commit -qm "init"
git checkout -q -b chore/export-format
cp -R "$here/fixtures/after/." .
