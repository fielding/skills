---
type: llm
focus: last_message
---

The fail policy is directional: fail closed when emitting a security decision, and let the
provider retry when we did not finish. A webhook provider treats 2xx as "delivered, never send
again", so a 200 must mean the event was actually handled (or is a known replay).

This check is only about the error path. The missing-secret branch and verification ordering
are graded elsewhere.

PASS if a thrown exception in the handler (a database error, an unexpected failure) produces a
500 so the provider retries, whether via a try/catch that responds 500, `next(err)` into an
error middleware, or an async wrapper that forwards rejections, and 200 is returned only for
success or a deterministic idempotent replay of an already-processed event.

FAIL if unexpected errors are caught and swallowed into a 200, if the handler returns 200
before the work has finished, or if a database failure is turned into a 2xx response.
