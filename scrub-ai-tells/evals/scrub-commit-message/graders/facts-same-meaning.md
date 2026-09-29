---
type: llm
focus: last_message
weight: 2
---

This is a scrubbed commit message. The original said, in substance: exponential backoff was
added to the export uploader; before, one 503 from the storage API failed the whole export;
retries are capped at 5 attempts so a dead endpoint cannot hang the job; partial uploads
(.part objects) are cleaned up on the final failure; two constants were added
(`RETRY_MAX_ATTEMPTS` default 5, `RETRY_BASE_MS` default 200); unit tests cover the backoff
schedule; it fixes #4821; Priya Natarajan is co-author.

This check is only about the facts. Rephrasing is fine; softening, dropping, or adding is not.
Register, narration style, and any commentary around the message are graded elsewhere.

PASS if every fact listed above is still present with the same meaning, no new fact appears,
and the bullet list and the trailer lines (Fixes / Co-Authored-By) survive.

FAIL if any fact is dropped or softened (the 503, the 5-attempt cap, the dead-endpoint reason,
the .part cleanup, a constant or its default, the tests), if a fact that was not in the
original appears, or if the bullets or the trailer were removed.
