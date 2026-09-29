---
type: llm
focus: last_message
weight: 2
---

Idempotency lives in the database. Two concurrent retries of the same event must not both get
past the guard, and the only thing that guarantees that is a uniqueness constraint enforced by
Postgres at insert time.

This check is only about the mechanism. Where the insert sits relative to other work, and
whether it is awaited, are graded elsewhere.

PASS if the `webhook_events` table (or its described shape) has a UNIQUE constraint or a
unique index on the provider event id, AND duplicates are detected by attempting the INSERT
and catching the unique violation (Postgres 23505, `ON CONFLICT DO NOTHING` with a rowcount
check, `ON CONFLICT ... RETURNING` with an empty result, or equivalent), then returning
idempotent success.

FAIL if duplicate detection is a SELECT for an existing row followed by an INSERT, if an
in-memory Set or Map of seen ids is the only guard, or if there is no unique constraint on
the event id.
