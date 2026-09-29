---
type: llm
focus: { source: file, path: ".handoff/NEXT.md" }
---

This is the NEXT.md a handoff wrote for a cold-start agent. Ground truth about the repo:

- HEAD has one commit: a TokenBucket rate limiter whose `_refill` uses `time.time()`. The
  commit message says CI saw a negative elapsed during an NTP step (#14) and the real fix
  is an injectable monotonic clock.
- The working tree has an UNCOMMITTED, half-finished version of that fix: `__init__` gained a
  `clock` parameter (default `time.monotonic`) and sets `self._last = self._clock()`, but
  `_refill` still reads `now = time.time()`. A new test, `test_refill_after_sleep`, drives a
  FakeClock and fails (tokens stay ~0 instead of refilling to 2.0). The other two tests pass.
- Tests run with `python3 -m unittest discover -s tests`; the README says not to use pytest.

A cold-start agent should be able to execute each item without asking, and should know why
it is doing it.

PASS if the items are concrete actions, each carrying a short WHY or a pointer to where the
reason lives (the commit message, #14, the failing test), not vague directions.

FAIL if the list is vague ("continue the work", "fix tests"), if the items are bare
imperatives with no reason and no pointer to one, or if the file is missing or empty.
