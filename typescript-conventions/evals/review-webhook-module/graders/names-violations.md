---
type: llm
focus: last_message
weight: 2
---

Six convention violations are planted. The review must name them with enough location detail
to find each.

1. Closed union / runtime schema drift: `SEND_OUTCOMES` (and `SendOutcome`) include
   `"rate_limited"` but `SendOutcomeSchema = z.enum(["sent", "blocked"])` does not, so a real
   vendor outcome fails parsing. Fix: extend both together; treat the union and the Zod enum as
   one edit (or derive one from the other).
2. Tri-state boolean in `SharingPanel.tsx`: `useFeatureFlag` returns `boolean | undefined`
   while loading, and `if (!enabled)` renders the legacy panel during the loading window.
   Fix: `if (enabled === undefined)` returns a loading/skeleton state; then `=== true`.
3. Fire-and-forget write: `db.deliveryLog.create(...)` is not awaited before
   `enqueueDelivery(event.id)` and the 200 response, but the delivery worker reads that row.
   Fix: await it (or make the consumer upsert idempotently / use a transactional queue).
4. Idempotency: dedupe is `findFirst` then `create` (SELECT-then-INSERT, two concurrent
   retries both pass), and it runs AFTER `classifyMessage`, an LLM call that is nondeterministic
   and can time out. Fix: UNIQUE constraint on `externalId`, insert and catch the violation,
   and run the replay check before the classifier.
5. Signature verification: `if (!secret) return true` fails open when the secret is
   unconfigured (must return 5xx), and `expected === header` is not constant-time (use
   `crypto.timingSafeEqual` after normalizing lengths).
6. Date-only string: `new Date(event.occurredOn).toLocaleDateString(...)` on "YYYY-MM-DD" is
   parsed as UTC midnight and renders a day early in western timezones. Fix: split/reformat
   the string or use a plain-date type.

PASS if at least FOUR of the six are identified, each with the file or function and a fix in
the convention's direction. Naming both halves of item 4 or item 5 is not required for that
item to count.

FAIL if three or fewer are identified, or if it fabricates code that is not in the fixture
(quoting functions, files or lines that do not exist). Additional legitimate findings beyond
the six (the `console.log` header/body dump, missing `code` fields, style) are fine and must
not cause a FAIL. Approving the `findFirst`-then-`create` dedupe, the `===` signature compare,
or the `if (!enabled)` guard as fine is a FAIL regardless of count.
