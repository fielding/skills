---
type: regex
target: { source: file, path: "draft.md" }
pattern: '—'
match: not_contains
weight: 2
---

The standing rule: every em dash is removed. The fixture had three.
