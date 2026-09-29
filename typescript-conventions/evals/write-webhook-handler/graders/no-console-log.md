---
type: regex
target: last_message
pattern: '\n\s*console\.log\('
match: not_contains
---

Anchored to a code line so a prose mention ("no `console.log`") does not count.
