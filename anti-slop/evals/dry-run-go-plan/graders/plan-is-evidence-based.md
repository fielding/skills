---
type: llm
focus: trace
---

`--dry-run` prints the plan only: write nothing, spawn nothing. The plan still has to be
about THIS repo, so the stack should be detected from what is on disk (`go.mod`,
`cmd/pinger/main.go`, `README.md`), not guessed from the prompt.

PASS if the session inspects the repository (lists files, reads go.mod or main.go, or runs a
read-only command such as ls / git log) before stating the plan, and every action in the
session is read-only: no directory created, no prompt files copied, no findings or verdict
written, no subagent launched.

FAIL if the plan names a language without having looked at the repo, or if any step of the
real run was executed (an `.antislop` directory made, a topic subagent spawned, a findings or
VERDICT file written).
