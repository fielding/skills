---
type: llm
focus: last_message
weight: 2
---

The learner said they are a Python developer and want intern-level depth. This is a large,
open-ended ask, so the skill's correct first move is to orient: find out what the learner
already knows so the teaching can be anchored to it. The session ends after this first reply.

PASS if the reply does either of these:
  (a) starts teaching by anchoring ownership/borrowing to something the learner knows from
      Python (names as references, aliasing a mutable list passed to a function, reference
      counting, `with` blocks) and names at least one place where that analogy breaks down; or
  (b) orients first with diagnostic questions that are tied to the learner's Python background
      (e.g. asks how they think about what happens when a list is passed to a function, or
      what they believe `del` / reference counting does), so the later anchoring can be built
      on their actual mental model.

FAIL if the reply asks only generic questions that ignore the stated Python background
("have you heard of the borrow checker?"), or teaches Rust in isolation with no Python
anchor and no statement of where an analogy stops holding.
