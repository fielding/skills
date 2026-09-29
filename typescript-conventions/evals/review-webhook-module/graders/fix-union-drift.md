---
type: llm
focus: last_message
---

Judge only the drift between `SEND_OUTCOMES` (includes `"rate_limited"`) and
`SendOutcomeSchema = z.enum(["sent", "blocked"])`. If the review does not mention it at all, answer FAIL: a planted violation the review skipped counts against this grader, not only against the coverage grader.

PASS if the recommended fix adds `rate_limited` to the Zod enum or derives the schema from the
const array (`z.enum(SEND_OUTCOMES)`), so the compile-time union and runtime schema are
maintained as one edit.

FAIL if the recommended fix is `z.string()`, widening `SendOutcome` to `string`, or removing
`rate_limited` from the array.
