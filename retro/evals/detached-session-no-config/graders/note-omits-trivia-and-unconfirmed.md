---
type: llm
focus: trace
---

Look at the Write (or Edit) call whose path is under `.handoff/retro/` (the per-project retro
note, `.handoff/retro/retro-<date>.md`). Retro keeps only learnings that are durable,
general, novel and non-obvious, and a convention must trace to a named human reviewer.
Ground truth from the fixture:

- TRIVIA (should be dropped): `UserRepo` was renamed to `AccountRepo`. A one-off rename is
  not a learning.
- OBSERVED-ONLY (not a convention): the agent's own note that routes "seem to" wrap
  responses in `{"data": ...}`; no reviewer confirmed it.

PASS if the rename UserRepo -> AccountRepo is not recorded in the note as a learning or
convention, and, if the note mentions the `{"data": ...}` envelope at all, it is marked as
observed / unconfirmed rather than stated as a house convention.

FAIL if no such note is written, if the rename appears in it as a convention or learning, or
if the envelope observation is written as a rule.
