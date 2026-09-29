---
type: regex
target: last_message
pattern: '#\[source\]|map_err'
---

The `#[from]` fix is `#[source]` plus explicit `.map_err` at the call site.
