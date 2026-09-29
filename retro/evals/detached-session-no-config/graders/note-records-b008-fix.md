---
type: llm
focus: trace
---

Look at the Write (or Edit) call whose path is under `.handoff/retro/` (the per-project retro
note, `.handoff/retro/retro-<date>.md`). Ground truth from the fixture: ruff B008 fires on
`Depends()` defaults in FastAPI signatures; the fix the session landed is
`Annotated[Session, Depends(get_db)]`, not adding B008 to the ignore list. That is a durable,
general lint gotcha and belongs in the note.

PASS if the note records the ruff B008 -> `Annotated[Session, Depends(get_db)]` fix (B008
and the Annotated form, or an unmistakable description of them).

FAIL if no such note is written, or if the B008 / Annotated learning is missing from it.
