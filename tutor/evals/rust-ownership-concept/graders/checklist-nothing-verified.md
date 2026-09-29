---
type: llm
focus: { source: file, path: ".tutor/Understanding-Checklist.md" }
---

This is the Understanding Checklist the skill writes at the start of a session on Rust
ownership and borrowing. Nothing has been taught, checked, or demonstrated yet, because the
session ends after the first reply, so no item can honestly be Verified. Whether the items are
scoped to ownership for a Python developer is graded elsewhere.

PASS if the file exists, is not empty, and no item is marked `Verified` (statuses such as
Not started / In progress / Unverified / To do / Explained, not yet checked are all fine).

FAIL if any item is marked `Verified`, or if the file is missing or empty.
