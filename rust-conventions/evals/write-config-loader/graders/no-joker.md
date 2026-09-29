---
type: regex
target: last_message
pattern: '[\s(<,=]Box<dyn (std::error::)?Error|use anyhow|[\s(<,=]anyhow::|use eyre|[\s(<,=]eyre::'
match: not_contains
---

No type-erased or crate-wide joker errors. Anchored to code contexts (preceded by whitespace
or a bracket) so a backticked prose mention does not count.
