---
type: llm
focus: last_message
---

Judge only the `.unwrap()` finding (the `Mutex::lock().unwrap()` calls in `inbox.rs`). If the review does not mention unwrap at all, answer FAIL: a planted violation the review skipped counts against this grader, not only against the coverage grader.

PASS if the recommended fix is `.expect("...")` carrying the invariant being asserted (or,
alternatively, propagating a typed error instead of panicking).

FAIL if the review says `.unwrap()` is acceptable here, says `.expect` would hide the
underlying error, or recommends `unwrap_or_default()` / swallowing the poison.
