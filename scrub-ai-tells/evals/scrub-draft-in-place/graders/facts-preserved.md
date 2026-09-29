---
type: regex
target: { source: file, path: "draft.md" }
pattern: '^(?=[\s\S]*1\.4s)(?=[\s\S]*300ms)(?=[\s\S]*40k)(?=[\s\S]*null timestamps)(?=[\s\S]*--since)'
---

Scrub never adds or drops facts. The latency numbers, the export size, the null-timestamp bug
the user documented, and the `--since` mention all have to still be there.
