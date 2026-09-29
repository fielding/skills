---
type: llm
focus: last_message
weight: 2
---

PASS if the reply does one thing and then stops to check: either a short set of diagnostic
questions, or a single first concept (e.g. the single-owner rule, or move semantics) at intern
depth, and it ends by asking the learner to restate, predict, or answer something.

FAIL if it covers ownership, borrowing, shared vs mutable references, lifetimes and the borrow
checker in one pass, or if it does not end with a question for the learner.
