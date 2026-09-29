---
type: llm
focus: trace
weight: 2
---

Look at the Write (or Edit) call whose path is under `.handoff/retro/` (the per-project retro
note, `.handoff/retro/retro-<date>.md`). Ground truth from the fixture: maya, the maintainer,
ruled in the PR #212 review that every alembic migration needs a real `downgrade()`; `pass`
is not acceptable; she had said the same on #188 and #197. Retro's rule: a stated convention
must trace to a named human reviewer with a source pointer.

PASS if that note records the every-migration-needs-a-real-downgrade() ruling attributed to
maya with a source pointer (PR #212 or the review file).

FAIL if no such note is written, if the ruling is missing from it, or if it appears without
the reviewer attribution or without a source pointer.
