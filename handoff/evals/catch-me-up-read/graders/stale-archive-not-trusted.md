---
type: llm
focus: last_message
weight: 2
---

`.handoff/archive/STATUS-2026-06.md` is an archived June snapshot that says "TLS
termination: done, using a self-signed dev cert". The current `.handoff/STATUS.md`
(2026-09-22) supersedes it: TLS termination is BLOCKED on ops issuing a wildcard cert
(OPS-4471) and kestrel currently listens plain HTTP.

PASS if the reply presents TLS as blocked / not done (it may mention the old dev-cert
state only as history that was superseded).

FAIL if the reply says TLS termination is done or working, or presents the June archive's
contents as the current state.
