---
type: llm
focus: last_message
---

Judge only the `todo!()` on `Command::Replay` in `cli::run`, a command a user can invoke. If the review does not mention it at all, answer FAIL: a planted violation the review skipped counts against this grader, not only against the coverage grader.

PASS if the recommended fix is to return an error instead of panicking (an
`Unconfigured` / `Unsupported` / `NotImplemented`-style `Err` variant, or an explicit
"not available yet" failure that does not crash the binary).

FAIL if the review says the `todo!()` is fine because replay is unfinished, or recommends
`unimplemented!()` / `panic!()` with a better message.
