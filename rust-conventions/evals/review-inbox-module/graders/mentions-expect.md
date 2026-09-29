---
type: regex
target: last_message
pattern: '\.expect\('
---

The fix for `.unwrap()` in these conventions is `.expect("<the invariant>")`, not `?` and not
"handle the error"; the review has to say so in code.
