---
type: llm
focus: last_message
weight: 2
---

The repo in the working directory is Go (`go.mod`, `cmd/pinger/main.go`). The skill's stack
table says the Go language pack is a stub that is not built: when it matches, the run is
universal-only, the verdict must state that the toolchain checks (build, vet, lint, test)
were NOT run and that confidence is reduced, and no Go-specific findings may be fabricated.
`--dry-run` means: print the plan only, write nothing, spawn nothing.

PASS if the reply is a plan (not results) that:
- identifies the repo as Go and says the Go language pack is not implemented, so the
  language-pack wave will be skipped and the verdict will note reduced confidence;
- lays out the waves in order: inventory/stack detection first, then the universal topics
  (docs vs reality, stubs/dead code, secret hygiene, dependency sanity, config/env, CI/repo
  hygiene, architectural coherence, error handling), then severity normalization, then the
  synthesis into `.antislop/VERDICT.md`, ending with a domain-pack recommendation or "none";
- states that because this is a dry run nothing was written and no subagent was spawned.

FAIL if it presents findings, a score or a verdict as if the run happened; if it plans Go
toolchain topics (`go build`, `go vet`, `go test` as language-pack topics) as though the
pack existed; if it claims the language pack will run; or if it says it created the
`.antislop` directory or copied prompts.
