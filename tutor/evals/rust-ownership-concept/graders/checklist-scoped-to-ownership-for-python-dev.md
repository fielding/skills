---
type: llm
focus: { source: file, path: ".tutor/Understanding-Checklist.md" }
weight: 2
---

This is the Understanding Checklist the skill writes at the start of a session with a Python
developer who wants to retain Rust ownership and borrowing well enough to explain it back.
Nothing has been taught yet; the checklist names what the learner will need to understand.

This check is only about scope. Whether anything is marked Verified is graded elsewhere.

PASS if the file is a checklist scoped to Rust ownership/borrowing for a Python developer,
with items along the lines of: the problem ownership solves, move vs borrow, shared vs mutable
references, where the Python analogies (reference counting, every name is a reference) break
down, a visual model, and connections back to Python. Not every one of those has to appear;
the items must be about this topic and this learner, each with a status.

FAIL if the checklist is generic boilerplate with no Rust or Python content, or is about a
different topic.
