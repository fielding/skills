---
type: llm
focus: last_message
weight: 2
---

The learner asked for an end-to-end walkthrough of auth.py that sticks. This is a large ask,
so the skill's correct first move is to orient, and the session ends after this first reply.

PASS if the reply ends with at least one question for the learner — either calibration
(what they already know about bearer tokens, HMAC signatures, this API) or a prediction about
a specific branch of the code ("what do you think happens when the Authorization header is
missing?") — and does not narrate every branch of the file in one pass.

FAIL if the reply explains the whole flow end to end without asking the learner anything.
