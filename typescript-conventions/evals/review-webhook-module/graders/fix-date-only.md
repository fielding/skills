---
type: llm
focus: last_message
---

Judge only `new Date(event.occurredOn).toLocaleDateString(...)` on a "YYYY-MM-DD" string. If the review does not mention it at all, answer FAIL: a planted violation the review skipped counts against this grader, not only against the coverage grader.

PASS if the recommended fix avoids parsing the date-only string as a UTC instant: split and
reformat the string, use a plain-date type (Temporal.PlainDate, date-fns parse, Luxon
`fromISO` with a zone), store it as-is, or append an explicit local time (`T00:00:00`).

FAIL if the recommended fix is `toISOString()` on the same `Date`, `toLocaleDateString` with a
`timeZone: "UTC"` option only, or if the review says the parsing is fine.
