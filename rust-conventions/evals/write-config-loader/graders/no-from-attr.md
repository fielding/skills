---
type: regex
target: last_message
pattern: '#\[from\]\s*[\w\n]'
match: not_contains
weight: 2
---

"Explicit conversion: `.map_err` + `#[source]`, never `#[from]`." Anchored to the attribute
followed by a type or newline (as in code), so a backticked prose mention does not count.
