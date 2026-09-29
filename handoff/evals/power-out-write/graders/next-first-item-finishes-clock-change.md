---
type: llm
focus: { source: file, path: ".handoff/NEXT.md" }
weight: 2
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

PASS if the first one or two items are about finishing this exact change: make `_refill`
use `self._clock()` (or equivalently finish the clock injection) so that
`test_refill_after_sleep` passes, then commit.

FAIL if the first items are about something else, if no item says to finish the clock
injection so the failing test passes, or if the file is missing or empty.
