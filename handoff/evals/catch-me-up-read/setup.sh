#!/usr/bin/env bash
# Copies this case's fixtures into the run's throwaway working directory.
# `claude plugin eval` runs this as you (not sandboxed) with cwd already set there.
set -euo pipefail
cp -R "$(dirname "$0")/fixtures/." .
