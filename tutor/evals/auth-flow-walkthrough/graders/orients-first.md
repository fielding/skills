---
type: llm
focus: trace
---

PASS if, before walking the code in detail, the agent establishes the learner's starting point
— asks what they already know about bearer tokens, HMAC signatures, or this API — or states
the session goal and creates the checklist before diving in.

FAIL if it opens with a full line-by-line explanation and never asks a diagnostic question.
