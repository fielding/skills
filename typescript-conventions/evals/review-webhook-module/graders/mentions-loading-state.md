---
type: regex
target: last_message
pattern: '=== undefined|undefined\b[^.\n]{0,60}\b(loading|skeleton|placeholder)|\b(loading|skeleton|placeholder)\b[^.\n]{0,60}undefined'
flags: i
---

The tri-state fix treats `undefined` as "loading", a distinct state, not as "off".
