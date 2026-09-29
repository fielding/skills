---
type: regex
target: last_message
pattern: '[\w)\]?]\.unwrap\(\)'
match: not_contains
weight: 2
---

Anchored to a preceding identifier or closing bracket so a prose mention in backticks
("I used `.expect` rather than `.unwrap()`") does not trip it; a call in code always does.
