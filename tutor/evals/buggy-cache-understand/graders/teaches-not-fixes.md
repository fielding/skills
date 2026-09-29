---
type: llm
focus: last_message
weight: 2
---

The learner explicitly asked to be taught, not to have the bug patched.

PASS if the reply teaches rather than fixes: it does not present a corrected cache.py or a
complete patch as its main content, it starts from the problem (stale numbers) rather than
from the solution, and it ends by asking the learner at least one question — either to gauge
what they already understand about the caching code, or to predict what the code does for a
concrete call.

FAIL if the reply's main content is a fix or diff, or if it explains everything in one
monologue and asks nothing.
