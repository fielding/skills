---
type: llm
focus: last_message
weight: 2
---

The fail policy is directional: fail closed when emitting a security decision. A webhook
handler that cannot verify signatures because `PROVIDER_WEBHOOK_SECRET` is unset must not
guess; it fails in a way that tells the operator something is misconfigured and makes the
provider retry later.

This check is only about the missing-secret branch. Verification ordering, the comparison
primitive, and generic error handling are graded elsewhere.

PASS if, when `PROVIDER_WEBHOOK_SECRET` is missing or empty, the handler responds with a 5xx
status or throws so the framework returns 5xx, and verification is never skipped.

FAIL if a missing secret skips verification and lets the request through, if it responds with
400 or 401, or if there is an environment-gated bypass (for example
`if (process.env.NODE_ENV !== 'production')`) that is the default branch.
