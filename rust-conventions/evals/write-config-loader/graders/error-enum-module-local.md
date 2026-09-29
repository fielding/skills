---
type: llm
focus: last_message
weight: 2
---

Judge only the shape of the error type in the code. The conventions: each module owns an
error type named `Error` (not `ConfigError` funnelled into a crate-wide sum, not a type alias
to a boxed error, not a `String`), derived with `thiserror::Error`, and every variant that
wraps a cause (the read failure, the parse failure) holds it in a field marked `#[source]`.
Whether `.map_err` is used, and whether `#[from]`, `.unwrap()`, `Box<dyn Error>` or `anyhow`
appear, is graded by separate regex graders; do not judge those here.

PASS if there is a module-local enum named `Error` derived with `thiserror::Error` whose
cause-wrapping variants carry the cause in a `#[source]` field.

FAIL if the error type is named for the module and funnelled into a crate-wide sum, is a
`String`/`&'static str`, is a boxed or type-erased alias, is not derived with thiserror, or
wraps its causes without `#[source]`.
