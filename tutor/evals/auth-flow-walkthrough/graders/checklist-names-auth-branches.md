---
type: llm
focus: { source: file, path: ".tutor/Understanding-Checklist.md" }
weight: 2
---

This is the Understanding Checklist the skill writes at the start of the session, after
reading auth.py. auth.py has these branches: no Authorization header (401), wrong scheme or
empty token (400), token that does not split into two base64url parts (400), HMAC signature
mismatch (401), expiry checked with a 30-second clock-skew allowance (401), a not-before
claim with the same allowance (401), and required scopes missing in require_auth (403).

This check is only about scope and specificity. Whether anything is marked Verified is graded
elsewhere.

PASS if the checklist is scoped to this auth flow (authenticate / require_auth, tokens,
signatures, scopes) and names at least three of the branches or edge cases above as things to
understand, each with a status.

FAIL if it only lists generic template headings with no auth.py specifics, names fewer than
three of the branches above, or invents branches that are not in the file.
