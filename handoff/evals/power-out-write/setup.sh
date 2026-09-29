#!/usr/bin/env bash
# Copies this case's fixtures into the run's throwaway working directory.
# `claude plugin eval` runs this as you (not sandboxed) with cwd already set there.
#
# This case needs two states: a committed baseline (fixtures/head) and a half-finished,
# uncommitted change on top of it (fixtures/worktree), so the agent has a real
# `git log` and `git diff` to reconstruct from.
set -euo pipefail
cp -R "$(dirname "$0")/fixtures/head/." .
git init -q
git -c user.email=e@x -c user.name=e add -A
git -c user.email=e@x -c user.name=e commit -qm "Add token-bucket rate limiter with wall-clock refill

Refill uses time.time() for now. CI saw a negative elapsed during an NTP step
(#14); clamped to zero as a stopgap. Real fix is an injectable monotonic clock."
cp -R "$(dirname "$0")/fixtures/worktree/." .
