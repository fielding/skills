---
type: llm
focus: last_message
---

Judge only the `#[error("...")]` Display strings on the error variants. The convention: a
chain-walking reporter prints each cause, so a variant's Display must not inline the wrapped
source. A `{path}` placeholder for a path field is fine; `{0}`, `{1}` or `{source}` referring
to the wrapped error is not.

PASS if no `#[error(...)]` string on a cause-wrapping variant prints the wrapped source.

FAIL if any variant's Display string embeds its source error (for example
`#[error("read failed: {0}")]` on a variant wrapping `std::io::Error`), or if the variants
have no Display strings because thiserror is not used.
