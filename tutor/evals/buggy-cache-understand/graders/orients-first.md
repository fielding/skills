---
type: llm
focus: trace
---

PASS if, before explaining the internals, the agent asks the learner what they already
understand about the caching code or about decorators/caching in general (a diagnostic
question), or gives a short problem framing and then checks understanding before going deeper.

FAIL if the agent goes straight into a full explanation of the code with no diagnostic
question anywhere in the session.
