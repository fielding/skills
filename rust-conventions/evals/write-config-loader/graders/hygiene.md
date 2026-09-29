---
type: llm
focus: last_message
---

Secondary conventions: imports, comments, tests, attributes.

PASS if: all `use` statements sit at the top of the file grouped std first, then external
crates, then crate-internal, with no `use` inside a function body; there is no `#[inline]`;
any comments explain a why (an invariant, a contract) rather than restating the next line (no
"// read the file" above `fs::read_to_string`); and if a test module is included it is a
sibling file (`#[cfg(test)] #[path = "config_test.rs"] mod tests;`) rather than an inline
`mod tests { ... }` at the bottom.

FAIL if any of those is violated. Omitting tests entirely is fine.
