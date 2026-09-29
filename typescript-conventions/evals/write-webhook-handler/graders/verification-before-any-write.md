---
type: llm
focus: last_message
---

The fail policy is directional: fail closed when emitting a security decision. An unverified
body is untrusted input; nothing about it may be persisted or acted on until the signature has
been checked.

This check is only about ordering. The missing-secret branch, the comparison primitive, and
generic error handling are graded elsewhere.

PASS if signature verification happens before the body is trusted for any database write or
external call: the INSERT into `webhook_events`, any enqueue, and any outbound request all come
after the signature check has succeeded.

FAIL if any database write or external call happens before the signature is verified, or if
the handler persists the event and only then checks the signature.
