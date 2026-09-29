---
type: llm
focus: last_message
weight: 2
---

Ground truth for the tix store in this repo:
- "Set up CI pipeline (GitHub Actions)" — priority 2, open, READY.
- "Add coverage gate to CI" — priority 1 (the highest), open, but BLOCKED by the CI pipeline
  issue; it does not appear in `tix ready`.
- "Write CONTRIBUTING.md" — priority 4, open, READY.

PASS if the reply recommends picking up "Set up CI pipeline (GitHub Actions)" (by title or
id) as the next thing to work on, and does not present the coverage gate as something to
start now. Mentioning that the coverage gate is blocked and will become ready after the CI
pipeline is done, or that CONTRIBUTING.md is also available, is good.

FAIL if it recommends "Add coverage gate to CI" as the next task (priority-first without
checking blocking), recommends CONTRIBUTING.md over the CI pipeline with no rationale tied to
the dependency, or does not name a specific issue.
