---
type: regex
target: { source: file, path: ".tix/issues.jsonl" }
pattern: '"type":"dep"'
match: count:1
---
