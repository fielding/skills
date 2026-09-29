---
type: llm
focus: trace
---

Look at the Write and Edit calls to files under `.handoff/retro/` (they are usually near the
end of the trace) and at the final assistant message; evidence from either counts.

Ground truth. Today's PR #231 session produced a NEW durable learning: under pytest-xdist
each worker is its own process, so a sqlite `:memory:` engine is never shared and seeded
data never reaches the test; the fix is a per-test file DB under `tmp_path`. It is not in
the existing note, so it belongs in today's note with a source.

PASS if the pytest-xdist / sqlite `:memory:` gotcha appears in today's note (or in an Edit
to the notes) as a new learning with a source (the PR #231 thread, the ci bot, or conftest).

FAIL if the xdist / sqlite learning is missing from what was written, or appears with no
source.
