---
type: regex
target: { source: file, path: "draft.md" }
pattern: '^(?=[\s\S]*tix export --filter "open-bugs" --format jsonl --out \./bugs\.jsonl)(?=[\s\S]*tix sync --verbose --since 2026-01-01)'
weight: 2
---

Both command lines in the fenced block must survive byte for byte. The double hyphens in
`--verbose` / `--since` are the trap: the skill's own text writes em dashes as `--`, and a
careless pass turns the flags into commas.
