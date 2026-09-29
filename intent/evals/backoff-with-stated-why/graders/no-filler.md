---
type: regex
target: { source: file, path: "intent.md" }
pattern: 'aims to|it[''’]s worth noting|in order to|might potentially'
flags: i
match: not_contains
---

"No filler, no hedging, no 'this PR aims to.'" Every line is something a reviewer can act on.
