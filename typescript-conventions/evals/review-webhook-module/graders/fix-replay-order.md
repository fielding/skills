---
type: llm
focus: last_message
---

Judge only the ordering of the dedupe relative to `classifyMessage` (an LLM call that can time
out). If the review does not mention that the dedupe runs after classification, answer FAIL: a planted violation the review skipped counts against this grader, not only against the coverage grader.

PASS if the recommended fix moves the replay/dedupe check before `classifyMessage` (and before
any other external or nondeterministic work), so a retry replays the original result.

FAIL if the review recommends keeping classification first, or caching the classification as
the fix for the ordering problem.
