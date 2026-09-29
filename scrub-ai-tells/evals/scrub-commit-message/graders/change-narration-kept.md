---
type: llm
focus: last_message
---

This is a scrubbed commit message. The original narrated a change: "previously a single 503
from the storage API would fail the whole export", and now retries with backoff handle it.
Because this is a commit message, that "previously X, now Y" framing is correct and the skill
keeps it; the rule about flattening narration into a description of current state applies to
docs and READMEs, not to commit messages.

This check is only about register. Whether every fact survives, and whether commentary
surrounds the message, are graded elsewhere.

PASS if the text still reads as a commit message that narrates the change, keeping the
before/after framing: the single-503 failure is still described as what used to happen, and
the retry/backoff as what the change does about it.

FAIL if the before/after narration was rewritten into a description of current behaviour only
(for example "The uploader retries with exponential backoff" with the old single-503 failure
no longer framed as the previous behaviour), or if the text no longer reads like a commit
message.
