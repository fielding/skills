---
type: llm
focus: { source: file, path: ".handoff/DECISIONS.md" }
---

This is the DECISIONS.md a handoff wrote. The repo's evidence for design decisions: the
commit message (wall clock was a stopgap; an NTP step made elapsed negative in CI, tracked
as #14; the real fix is an injectable monotonic clock) and the working-tree docstring (the
clock is injectable so tests drive time deterministically instead of monkeypatching
`time.monotonic`, which was flaky when the suite ran in parallel).

PASS if it records the move from wall clock to a monotonic, injectable clock WITH the reason
(NTP step / negative elapsed / #14, and/or deterministic tests without monkeypatching), i.e.
the non-obvious "why", not just a restatement of the code.

FAIL if it only lists what the code does with no reasons, invents decisions that have no
basis in the repo, or is missing/empty.
