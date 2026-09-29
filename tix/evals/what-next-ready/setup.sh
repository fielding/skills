#!/usr/bin/env bash
# Copies this case's fixtures into the run's throwaway working directory.
# `claude plugin eval` runs this as you (not sandboxed) with cwd already set there.
#
# Then seeds a tix store with three issues and one blocking dependency, using the CLI so the
# store format always matches the installed tix. Ground truth for the graders:
#   A "Set up CI pipeline (GitHub Actions)"  p2  ready
#   B "Add coverage gate to CI"              p1  BLOCKED by A (highest priority, but not ready)
#   C "Write CONTRIBUTING.md"                p4  ready
set -euo pipefail
cp -R "$(dirname "$0")/fixtures/." .
git init -q && git add -A && git -c user.email=e@x -c user.name=e commit -qm init
tix init --prefix fk >/dev/null
A=$(tix add "Set up CI pipeline (GitHub Actions)" -p 2 -t infra -q \
  -b "Run lint + tests on every push. Needed before any coverage enforcement can exist.")
B=$(tix add "Add coverage gate to CI" -p 1 -t infra -q \
  -b "Fail the build under 85% line coverage. Requires the CI pipeline to exist first.")
tix add "Write CONTRIBUTING.md" -p 4 -t docs -q \
  -b "How to set up a dev env, run tests, open a PR." >/dev/null
tix dep add "$A" blocks "$B" >/dev/null
