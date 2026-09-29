---
type: llm
focus: last_message
---

The user asked for only the scrubbed commit message, with no commentary before or after it.
The message itself is a subject line, body paragraphs, a bullet list, and Fixes /
Co-Authored-By trailer lines. Whether the message's content is right is graded elsewhere.

PASS if the reply contains nothing outside the message itself: no preamble such as "Here is the
scrubbed message", no closing note, and no list or summary of the edits made. A code fence
wrapping the message is fine.

FAIL if anything other than the commit message appears in the reply, such as an introductory
sentence, an explanation of the changes, or a list of removed phrases.
