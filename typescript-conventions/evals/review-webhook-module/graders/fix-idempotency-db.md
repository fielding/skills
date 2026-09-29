---
type: llm
focus: last_message
---

Judge only the dedupe mechanism (`findFirst` on `externalId`, then `create`). If the review does not mention the dedupe race at all, answer FAIL: a planted violation the review skipped counts against this grader, not only against the coverage grader.

PASS if the recommended fix is a UNIQUE constraint (or unique index) on the external event id
and attempting the insert, catching the unique violation and returning idempotent success
(or `ON CONFLICT DO NOTHING` with a rowcount check).

FAIL if the recommended fix is still check-then-insert (even inside a transaction without a
lock), an in-memory seen-set, or a distributed cache lookup as the only guard.
