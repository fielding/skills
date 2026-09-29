---
type: regex
target: last_message
pattern: 'UNIQUE|unique (index|constraint|violation)|23505|ON CONFLICT'
flags: i
---

Idempotency lives in the database: a UNIQUE constraint (Postgres error 23505 / ON CONFLICT),
not an application-level existence check.
