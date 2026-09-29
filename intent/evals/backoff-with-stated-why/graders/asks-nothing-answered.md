---
type: llm
focus: last_message
---

The prompt supplied the Why, one Decision, and two Scope-Out items, and the diff shows the
What. "Never ask what the diff already shows"; only ask about intent that is not recoverable.

PASS if the final reply reports that intent.md was written (and where), summarises or shows
its content, and does not ask the user to supply the motivation, the jitter decision, or what
changed in http_client.py. Asking one genuinely open question (e.g. whether the AWS post should
be linked, or whether the key rotation needs its own follow-up) is acceptable.

FAIL if the reply asks the user why the change was made, what the change does, or which
jitter strategy was chosen, or if it says it could not proceed because no transcript was found.
