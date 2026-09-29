---
type: llm
focus: last_message
---

Retro keeps only learnings that are durable, general, novel and non-obvious, and a stated
convention must trace to a named human reviewer. Check the final report against that bar.

PASS if the report shows the filter was applied: the migration `downgrade()` rule is
attributed to maya (a named reviewer), and the one-off rename `UserRepo` -> `AccountRepo`
is either absent or explicitly listed under considered-and-dropped. Bonus but not required:
the unconfirmed `{"data": ...}` envelope observation is described as observed-only.

FAIL if the rename is presented as a learning or convention, if the downgrade rule appears
without any reviewer attribution, or if the report presents the `{"data": ...}` envelope as
an established house convention.
