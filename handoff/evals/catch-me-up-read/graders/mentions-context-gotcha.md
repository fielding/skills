---
type: llm
focus: last_message
---

The repo's `.handoff/CONTEXT.md` holds the environment gotchas a returning developer needs:
Go 1.23 is required (`slices.Chunk`), brew go is 1.22 so use mise; `go test` needs
`-count=1`; the staging upstream is reached by IP, 10.4.0.12:8080. A catch-me-up summary
should carry at least one of these forward.

PASS if the reply mentions at least one CONTEXT gotcha: Go 1.23 / mise, `-count=1`, or the
IP upstream 10.4.0.12:8080.

FAIL if none of those three gotchas appears in the reply.
