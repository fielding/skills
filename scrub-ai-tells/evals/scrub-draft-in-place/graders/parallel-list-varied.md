---
type: regex
target: { source: file, path: "draft.md" }
pattern: '- Enables [^\n]*\n- Enables [^\n]*\n- Enables'
match: not_contains
---

The three "Enables ..." bullets shared one grammatical skeleton; at least one must be rephrased.
