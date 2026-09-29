---
type: llm
focus: last_message
---

Judge only the missing-secret branch of `verifySignature` (`if (!secret) return true`). If the review does not mention the missing-secret case at all, answer FAIL: a planted violation the review skipped counts against this grader, not only against the coverage grader.

PASS if the recommended fix makes a missing or empty `VENDOR_WEBHOOK_SECRET` respond with a
5xx status (or throw so the framework returns 5xx), so misconfiguration is loud and the
provider retries.

FAIL if the recommended fix is to `return false` (which turns misconfiguration into a quiet
401 "bad signature"), to return 400/401/403, to log and continue, or to add an environment-
gated bypass as the default branch.
