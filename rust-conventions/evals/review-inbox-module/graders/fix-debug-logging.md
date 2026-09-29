---
type: llm
focus: last_message
---

Judge only the PII/secret finding: `#[derive(Debug)]` on `InboundMessage` (holds the user
`body` and a bearer `reply_token`) and `tracing::warn!(?msg, ...)` logging it whole. If the review does not mention the Debug derive or that log line at all, answer FAIL: a planted violation the review skipped counts against this grader, not only against the coverage grader.

PASS if the recommended fix stops the payload from reaching the log: a hand-written `Debug`
that keeps `id` (and maybe `body.len()`) but drops `body`, and/or a redacting wrapper type for
`reply_token` (e.g. `secrecy::SecretString`), and/or removing the `?msg` from the log line.

FAIL if the only recommendation is to lower the log level while still logging the derived
Debug, or if the review says the derived Debug is fine.
