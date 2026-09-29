# anti-slop evals

Native `claude plugin eval` cases, run across models by skillbench
(`~/src/hack/skillbench`). Each case is one `claude -p` turn in a sandbox with no network, a
throwaway HOME, and only this skill loaded; the scaffold (`setup.sh`) copies `fixtures/` into
the working directory and makes it a one-commit git repo.

- `quick-reality-check`: the full orchestration on a tiny Python "notekeeper" CLI whose README
  makes confident claims. Planted: the AES-256 "encrypted at rest" feature is a stub
  (`crypto.py` raises NotImplementedError), a hardcoded `sk-live-...` key in `cli.py`, theater
  tests, no lockfile. `--quick` so the Python language pack must be skipped and no toolchain
  is needed. Graders assert the artifacts (`.antislop/VERDICT.md`, stack map, per-topic
  findings), the verdict's score line and Go/No-Go, both planted flags in the red flags with
  the key redacted, a score below 60 and NO-GO, at least six subagent spawns, and that no `py0x`
  prompt was handed to a subagent. Subagent graders are trace regexes over the tool_use name
  (`Task` in current Claude Code, `Agent` in older builds); `tool_used: Agent` never matched.
  Needs Bash, Write and the Agent tool; it spawns ~10 subagents, so it is the expensive case.
- `dry-run-go-plan`: `--dry-run` on a Go repo. The Go pack is stubbed, so the plan must say
  universal-only with reduced confidence, and dry-run means nothing written, nothing spawned.

Sandbox caveat: the skill locates its `references/` under `~/.claude/skills`, which does not
exist in the sandbox; the orchestrator has to find the plugin's own directory instead. The
orchestration grader tolerates that recovery.

Run: `cd ~/src/hack/skillbench && uv run skillbench run -s anti-slop -m claude-haiku-4-5 --runs 1`
