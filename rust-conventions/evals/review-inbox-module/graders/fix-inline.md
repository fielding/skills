---
type: llm
focus: last_message
---

Judge only the `#[inline]` on `Inbox::new`. If the review does not mention `#[inline]` at all, answer FAIL: a planted violation the review skipped counts against this grader, not only against the coverage grader.

PASS if the recommendation is to remove the attribute and let the compiler decide.

FAIL if the review says to keep it, add `#[inline(always)]`, or add `#[inline]` elsewhere.
