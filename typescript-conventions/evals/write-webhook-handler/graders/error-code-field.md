---
type: regex
target: last_message
pattern: '\bcode:\s*["''][A-Za-z][A-Za-z0-9_-]{3,}["'']'
---

API errors carry a machine-readable code (`{ error: "...", code: "BAD_SIGNATURE" }`). Any
casing or hyphenation counts; the assertion is that a `code` field exists at all.
