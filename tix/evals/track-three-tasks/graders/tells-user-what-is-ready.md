---
type: llm
focus: last_message
---

The user wanted to "see what's unblocked". Ground truth after correct setup: A (retry) and
C (README) are ready; B (--retries flag) is blocked until A is closed.

PASS if the reply tells the user that the flag issue (B) is blocked by the retry issue (A)
and that the other two are ready to pick up — for example by showing or paraphrasing
`tix ready` output — and reports the created issue IDs or titles.

FAIL if it says all three are ready, says B is ready, or gives no indication of what is
unblocked.
