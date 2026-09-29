---
type: llm
focus: last_message
---

Judge only the HMAC comparison `expected === req.header("x-vendor-signature")`. If the review does not mention the comparison at all, answer FAIL: a planted violation the review skipped counts against this grader, not only against the coverage grader.

PASS if the recommended fix is `crypto.timingSafeEqual` on two buffers, with a length check or
normalization before the compare.

FAIL if the review recommends keeping `===`, a manual character loop, or comparing strings
after lowercasing.
