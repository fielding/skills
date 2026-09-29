---
type: regex
target: last_message
pattern: '\n\s*#\[inline'
match: not_contains
---

An attribute in code sits on its own line; a prose mention does not.
