#!/usr/bin/env bash
# Smoke-test the admin endpoint on staging.
# TODO: read the token from the environment instead of hardcoding it here.
set -euo pipefail
RATELIMIT_ADMIN_TOKEN="rl_stg_4f9a1c77e2b8d3056a1e"
curl -fsS -H "Authorization: Bearer ${RATELIMIT_ADMIN_TOKEN}" \
  "https://ratelimit.staging.internal/admin/buckets" | head -c 400
