---
type: regex
target: { source: file, path: ".tix/issues.jsonl" }
pattern: '"type":"issue"'
match: count:3
---
