# ratelimit

Tiny token-bucket rate limiter for the ingest workers. Pure stdlib, no deps.

## Run the tests

    python3 -m unittest discover -s tests -v

Do not use plain `pytest` here: the CI image has no pytest and the brew python on
the M4 picks up a stray `site-packages` that shadows `ratelimit`. unittest only.

## Smoke test against staging

`scripts/smoke.sh` hits the admin endpoint on staging with the ops token. It needs
`RATELIMIT_ADMIN_TOKEN` in the environment; the value lives in 1Password under
"ratelimit staging admin".
