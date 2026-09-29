---
type: llm
focus: { source: file, path: "intent.md" }
---

This is the intent.md for an uncommitted change on branch fix/retry-backoff. The user stated
these in the prompt, and they are the only legitimate source for them:

- Why: the vendor rate-limits the Tuesday batch; fixed delays make every worker retry in
  lockstep so the batch stampedes the API and gets a second round of 429s.
- Decision: full jitter over decorrelated jitter, because it is simpler and the AWS
  architecture post shows it within a few percent at their volume.

PASS if Why is the rate-limit / lockstep-stampede / 429 reason and Decisions records full
jitter over decorrelated jitter with the stated reason, neither invented nor changed.

FAIL if Why or the jitter decision is missing, invented, or altered from what the user said.
