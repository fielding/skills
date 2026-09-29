---
type: llm
focus: last_message
weight: 2
---

The repo has a `.handoff/` directory with four docs. NEXT.md lists, in order: (1) wire
`--upstream-timeout` into `proxy/dial.go` because a hung upstream held a worker 11 minutes
in prod; (2) add a regression test with httptest; (3) enable TLS once OPS-4471 lands.
STATUS.md agrees: the `--upstream-timeout` flag is parsed but not passed into the dialer in
`proxy/dial.go`. The user asked what to pick up first.

PASS if the reply names wiring `--upstream-timeout` into `proxy/dial.go` (or the dialer) as
the first thing to pick up.

FAIL if it names something else as the first action (TLS, the regression test, something
inferred from the code rather than the docs), or gives no first action at all.
