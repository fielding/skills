---
type: llm
focus: trace
weight: 2
---

Look at the Write and Edit calls to files under `.handoff/retro/` (they are usually near the
end of the trace) and at the final assistant message; evidence from either counts.

Ground truth. The existing note `.handoff/retro/retro-2026-08-12.md` already records
"Migrations must be reversible (maya, PR #188), Seen: 1x". In today's PR #231 thread maya
repeats that exact ruling (third time). Phase 2's novelty check means grepping the existing
note first: a repeat is a recurrence, so the existing entry gets its Seen counter bumped
and/or PR #231 added as a source, not a duplicate entry.

PASS if the reversible-migrations ruling is treated as a recurrence: its Seen counter is
bumped (e.g. "Seen: 2x") and/or PR #231 is added as another source, in the old note or the
new one, rather than written as a fresh standalone entry with no reference to the existing
one.

FAIL if the migrations ruling is duplicated as a brand-new entry with no reference to the
existing one, or if neither a counter bump nor an added #231 source appears anywhere.
