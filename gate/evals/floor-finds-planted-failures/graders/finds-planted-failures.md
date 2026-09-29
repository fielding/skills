---
type: llm
focus: trace
weight: 2
---

The branch under gate carries one commit, "wip: bulk discount tiers", with two planted
floor failures. Ground truth:

1. Lint: `src/shoplite/pricing.py` imports `json` and never uses it; `ruff check .` reports
   F401 on that line. Formatting is clean.
2. Test: `tests/test_pricing.py::test_bulk_discount_at_threshold` fails. It expects 10 units
   at 250 cents to total 2250 (10% off), but `bulk_discount_cents` uses
   `line.qty > BULK_THRESHOLD`, so exactly 10 units gets no discount and the total is 2500.
   intent.md's Decisions say the threshold is inclusive, so the code, not the test, is wrong.
   The other four tests pass.

The repo's AGENTS.md Gate section declares the floor commands (`.venv/bin/ruff check .`,
`.venv/bin/ruff format --check .`, `.venv/bin/pytest -q`).

PASS if the session actually runs ruff and pytest (the declared commands or a clear
equivalent) and reports BOTH failures: the unused `json` import in pricing.py, and the
failing `test_bulk_discount_at_threshold` (identifying the off-by-one / `>` vs `>=` against
the inclusive-threshold decision is a plus, not required).

FAIL if it reports the floor as green, misses either failure, reports a failure that does not
exist (formatting, other tests), applies a fix to the source, or never runs the commands and
reasons about the code instead.
