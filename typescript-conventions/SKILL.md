---
name: typescript-conventions
description: >-
  Battle-tested TypeScript conventions for writing and reviewing TypeScript.
  Covers the directional fail policy (fail closed when emitting, degrade
  gracefully when ingesting), closed unions with paired runtime schemas,
  tri-state boolean guards, null-safety at query boundaries, the date-only
  string UTC pitfall, fire-and-forget race bans, DB-enforced idempotency
  ordered before nondeterministic checks, JSONB merge-not-overwrite,
  feature-flag enforcement at every layer, React single-source-of-truth and
  narrow cache invalidation, deterministic test identifiers, and
  PII/secret-free structured logging. Cross-references
  state-space-minimization for the language-agnostic state-shrinking
  principles. Use when writing or reviewing TypeScript code (*.ts, *.tsx,
  package.json) in a project that has not already declared its own
  conventions.
allowed-tools: Read, Grep, Glob, Bash, Skill
---

# TypeScript Conventions

A baseline of TypeScript conventions distilled from production incidents and high-bar reviews. Two layers:

1. **General principles** (any language, but stated here in their TypeScript expression). The `rust-conventions` pack restates the same ideas in Rust's idiom.
2. **TypeScript idioms** (the specific mechanism the language and its ecosystem give you).

Defer to a project's own conventions where it has declared them; use these to fill the gaps.

> The state-shrinking principles -- parse-don't-validate, drop speculative tolerance, validate at the boundary, no dead or speculative code -- are owned by the **`state-space-minimization`** skill. This skill does not restate them. Invoke `state-space-minimization` alongside this one when writing or reviewing; the two compose. Where a convention below is a TypeScript mechanism *for* an SSM principle, it says so and points back.

---

## General principles (TypeScript expression)

### The fail policy is directional

**Fail closed when emitting; degrade gracefully when ingesting.**

- *Emitting* -- auth checks, signature verification, safety/compliance gates, generated content shown to users: on error or timeout, default to the blocking decision. A gate that fails open is not a gate.
- *Ingesting* -- vendor webhooks, third-party payloads: validate advisorily. When a partial payload is still actionable, accept and warn rather than hard-reject; a strict boundary schema that drops whole payloads turns an upstream vendor bug into silent data loss. Persist unprocessable events in a dead-letter store, and alert on gap metrics (events initiated vs processed), not just error rates.

The refinement on the ingest side: distinguish **advisory** validation (fast, deterministic, fails open, never blocks the user) from **enforcement** validation (runs once at the commit point, fails closed). Client-side checks are UX only; the server-side gate is the real guard, so client-check failures degrade silently.

### One canonical home per fact

Store a relationship as a foreign key on the record itself; every consumer derives context from one lookup. When the same concept scatters across columns or state stores with overlapping ownership, every fix creates new routing edge cases. Define canonical semantics before adding another field. (SSM: normalize so each fact has one determinant.)

### Emission is not implied by persistence

Every state-mutation path -- API handler, webhook, background job, each new ingress route -- must explicitly emit the same domain/analytics events. A refactor that moves persistence timing moves the emissions with it. Operational metrics, product analytics, and audit logs are *separate systems*: a user-facing action emits to each that applies, and none substitutes for another. Include the canonical correlation ID in every lifecycle event at every point where it is known.

### Comment only the why

Terse code over narration. Drop any comment that restates what the next line does; keep the non-obvious why: an invariant, a race rationale, a boundary contract, the result of an empirical probe. A code comment does not mitigate a race condition -- fix the race.

---

## Types

### Closed unions, extended explicitly

Model finite outcomes as literal unions (`type SendOutcome = "sent" | "blocked" | "rate_limited"`), and when a new case appears, extend the union -- never widen to `string`. When a value participates in both a compile-time union and a runtime schema (a `const` object and its Zod enum), adding a member means updating both; treat them as one edit.

### Tri-state booleans are branched explicitly

Anything loaded asynchronously (feature flags before a profile loads, config before hydration) is `boolean | undefined`. Branch with `=== true` or `?? false`, never truthiness, and treat `undefined` as "loading" -- a distinct UI/logic state -- not as "off". Rendering on the default-false value and re-rendering when the real value arrives causes both visible flashes and wrong logic paths.

```typescript
const enabled = useFeatureFlag("patient-sharing"); // boolean | undefined
if (enabled === undefined) return <Skeleton />;    // loading is its own state
if (enabled) { /* ... */ }
```

### Never hand-edit generated files

Generated types (DB schemas, API clients) encode a contract owned by the generator. Fix call sites to match, or change the source schema and regenerate; CI drift checks make manual edits an infinite regenerate-overwrite loop.

### Typed event helpers

One interface per analytics/domain event plus a typed `trackXxx(props)` helper. No ad-hoc string-and-object emission -- the type is what keeps every emission site consistent when the event grows a field.

### Dual-layer validation for external and LLM-produced enums

Zod (or equivalent) at the parse boundary **and** a DB CHECK constraint. Neither alone suffices: the DB misses application-logic errors, the app misses direct writes. Parse-time validation is what makes any downstream `as` cast legitimate. (SSM: parse, don't validate.)

### API errors carry a machine-readable code

`{ error: "human message", code: "PHI_DETECTED" }`, with the status code chosen per failure class. Callers branch on `code`, never on message text.

---

## Null and absence

### Handle null at every external access

Data crossing a boundary (query results, parsed payloads, URL fragments) gets `?.` and `??` at the access site:

```typescript
return sections?.length ?? 0;
const visitId = page.url().split("/").pop() ?? "";
```

### Match query cardinality to reality

Never use fetch-exactly-one APIs (`.single()`, `firstOrThrow`) where zero rows is a legitimate outcome; use the maybe/limit variants (`.maybeSingle()`, `LIMIT 1`). A read path must also tolerate duplicates if the write path doesn't structurally prevent them.

### Nullable external fields are modeled, not discovered

Declare them (`z.string().nullish()`) and handle null with an explicit, logged early-return. Error messages must distinguish "malformed payload" from "valid payload with an expected null" -- strict schemas that silently drop null-bearing payloads are a data-loss bug, not rigor.

### In gate logic, null means "blocked"

A null/absent sequence value must read as "not yet happened", never as a valid fresh state. Distinguish "pending response" from "response received but unconsumed"; conflating them bypasses the gate on first use.

---

## Validation gotchas

### Never parse date-only strings with `new Date()`

JavaScript interprets `"2000-01-01"` as UTC midnight, so `toLocaleDateString()` shifts it back a day in western timezones. Split and reformat the string, or use a date library's plain-date type. (Classic symptom: birth dates rendering one day early.)

### Regex validates shape, not semantics

`\d{4}-\d{2}-\d{2}` accepts `9999-99-99` and `2001-02-29`. Values that carry meaning -- dates, ranges, identifiers with checksums -- need semantic validation at the boundary, especially when an LLM produced them.

### Strict canonical formats double as injection defense

Where a field has a tight canonical format (E.164 phone numbers: `+` then 1–15 digits), enforce it strictly *before* the value is serialized into any markup or query context. The restricted character set structurally prevents injection; treat the format check as a security control, not data hygiene, and resist permissive regexes.

---

## Async, races, idempotency

### No fire-and-forget writes on depended-on paths

If any later event (a webhook, a job, a user action) depends on a write, that write completes synchronously before responding -- or the consumer upserts idempotently, or a transactional queue guarantees ordering. Evaluate every deliberate exception as race-window probability × user-visible impact, and write that reasoning down.

### Idempotency lives in the database and runs first

- Enforce with a UNIQUE constraint on the external event/message ID; catch the violation and return idempotent success. SELECT-then-INSERT is a race, not a guard (two concurrent retries both pass the SELECT). Add advisory locks when retries must serialize.
- Replay checks run **before** anything nondeterministic -- an LLM classifier, an external call, anything that can time out. A retry must replay the original result, never get re-judged.
- Idempotency guards also run before enqueueing async work, or retries fan out duplicate jobs.
- Deliberate retries mint fresh idempotency keys (or dedupe swallows the retry); first-run jobs keep stable ones.

### One writer per field, or explicit coordination

Multiple writers to the same field need a single canonical writer, locking, or a pending-marker cleared only on confirmed success. An inferred decision (LLM heuristic, derived state) must never override an explicit one (user action, tool call) without comparing timestamps or sequence numbers.

### Guard against stale async responses

- UI reading async results keeps a monotonic request counter (or token-identity ref for auth): apply a response only if it is still the latest.
- Submit buttons that trigger async validation get an in-flight lock, released on **every** exit path -- especially when each request mints a fresh idempotency key, since duplicate submissions then legally bypass backend dedupe.

### Fallback paths check before creating

An error/fallback handler that creates a resource must first check whether the primary path already created it -- otherwise a unique-constraint violation turns the fallback into a crash. On collision, reuse the existing row.

### Shutdown clears timers before releasing pools

A lingering `setInterval` that lazily re-creates connections resurrects workers on a system that is shutting down. Clear every timer first, and give connection factories a shutdown guard.

### Atomicity across steps

Wrap multi-step record creation in one transaction (or a stored procedure). Where a true transaction cannot span an external call, use compensating rollback: write, call, delete-on-failure. Inside multi-step pipelines, wrap non-essential steps in their own try/catch with a skip fallback so a transient failure doesn't abort the whole pipeline through the outer catch.

### Verify counter bases empirically

Before writing threshold logic against a library's retry/attempt counter, confirm whether it is 0- or 1-based from behavior, not assumption -- then capture the probe result in a comment.

---

## Webhooks and external boundaries

- **Signature validation fails closed and runs first.** A missing or misconfigured secret returns 5xx -- never silently accepts unsigned requests. Dev bypasses require explicit environment gates and are never the default branch.
- **Compare HMACs with `crypto.timingSafeEqual()`** (after normalizing buffer lengths), never `===`.
- **Default to 500 on unexpected errors so the provider retries; reserve 200 for deterministic rejections** -- paired with idempotency so the retry is safe. Returning 200 with partially-committed state is silent data loss. For unrecognized senders, a silent 200 avoids advertising which endpoints are live.
- **Design for optional vendor fields with layered fallbacks**, and never gate one field's recovery on an unrelated field's absence. When an entity's ID changes from provisional to permanent across services, store both; key durable operations and uniqueness on the permanent one.
- **Per-integration requirements live in a vendor→config registry**, not scattered conditionals.

---

## Data layer

- **Never update a JSONB/metadata column with a whole object** -- that is a full overwrite destroying sibling keys written by other flows. Use a DB-level merge (`coalesce(col, '{}'::jsonb) || $1`, `jsonb_set`) or explicit fetch-merge-write; prefer the atomic DB merge under concurrency.
- **Audit every `ON DELETE CASCADE` foreign key before building delete or merge features**; explicitly reassign references to the surviving entity first. Cascades destroy dependent records silently and the loss surfaces late.
- **Soft-delete is a write-side change requiring read-side filters at every layer**: row-security policies, application queries, search functions, integrations. Without the read paths it is invisible.
- **Lifecycle state is an enum with timestamp and provenance, not a boolean.** A boolean cannot represent unknown / declined / revoked / re-granted, and you will need all four.
- **Defer record creation until the data exists.** No placeholder records to enrich later -- accurate absence beats fake data -- and never auto-link identity on a single shared attribute (a phone number is not a person).
- **Row-level security is a real boundary but never the only one.** Service-role paths bypass it; every endpoint and background job also filters by tenant in code. Every exposed table -- junction tables included -- needs explicit per-role policies.
- **Before merging a restructured query, `EXPLAIN ANALYZE` on realistic data.** A JOIN + `coalesce()` + leading-wildcard `ILIKE` can suppress the index selectivity a two-step lookup had.

---

## Feature flags

- **Assume flags gate backend behavior, not just UI** -- prompts, endpoints, cache keys, parsing paths. When functionality is "missing", check flag state before debugging deeper.
- **Enforce at every layer where behavior changes.** Hiding the UI while the backend never checks the flag silently enables the feature server-side; add guard clauses at the decision points.
- **Pin flag state in test fixtures explicitly**, and keep at least one legacy-path test alive so rollback doesn't rot. Never hard-code a flag value in a component -- it silently defeats rollout logic.
- **Handle the async loading window** (see tri-state booleans above): defer rendering or show a placeholder; don't flash the default.
- **A kill switch must not disable internal reconciliation paths** (status callbacks, delivery reconciliation) the system still exercises. Trace both user-facing and internal flows before early-returning on a flag.
- **Use flags for risky migrations**: both paths live, parse failures of the new path degrade to a safe default (never raw model output), instant rollback. Remove the dual path only with a clear cutover and rollback story, and document which backend behavior each flag controls.

---

## React and frontend state

(Applies when the project renders UI; the cache rules generalize to any client-side query layer.)

- **One source of truth for shared UI state.** Never mix query-cache state, local state, and optimistic writes for the same data -- that combination is a flickering-bug factory.
- **Centralize data loading**: one query/effect loads a collection; per-item queries in per-item components cause staggered loading, N re-renders, and layout shift. Thin presentational components render props; data hooks own fetching; consumers import only from a module's `index.ts`.
- **Invalidate narrowly.** Targeted keys with `exact: true`; never nuke a namespace. Cache keys include every scoping dimension (tenant, user). `staleTime: Infinity` requires an explicitly wired invalidation path. An update-in-place normalized cache cannot introduce new entities, so list queries need a refetch trigger, not cache patching. Realtime refetch triggers must watch every table a query joins, not just the primary one.
- **No optimistic updates without a reconciliation story.** A naive optimistic insert races the server response into duplicates or appear/disappear artifacts; wait for the response unless you can reconcile.
- **Prefer event-driven invalidation over polling** (DB trigger → pub/sub → targeted invalidation), and scope triggers to the exact columns and conditions clients display.
- **Hook dependency arrays are correctness, not style.** Depend on exactly what changes; wrap handlers in `useCallback` before listing them. Re-render loops are a root-cause bug category.
- **Clamp windowing/virtualization indices at both bounds** -- `Math.min(len, Math.max(0, i))`. Spacer math overflows silently and an overflowed start index propagates into the end index.
- **Reserve fixed space for transient UI** (spinners, typing indicators, streaming content) so it cannot shift layout; clean up every timer; give animation paths a show-everything fallback.
- **On ownership transfer, invalidate both sides** -- the old owner's client has stale data it may no longer be allowed to hold.
- **When a component-library wrapper fights the spec, drop to the primitive library it wraps** rather than forking the wrapper or adding a dependency.

---

## Logging and secrets

- **No `console.log` in application code** -- a structured logger with explicit fields, so redaction is possible at all.
- **Logs are a compliance boundary, in every environment and at every level.** No environment dumps, no secrets, no PII -- sanitize before the logger via field whitelisting, never rely on downstream access controls or "temporary" status. An env/request dump is a ship-stopper in review, not a nit.
- **Redact fully; never truncate.** The first 50 characters of a sensitive field still leak. Replace the value with a placeholder. Hash or mask identifiers before any third-party/analytics egress.
- **Opaque generated IDs are not PII** -- keep them; removing them breaks traceability for zero security gain. (Same judgment as Rust's redacted-Debug rule: redact genuine secrets, keep the correlation handles.)
- **LLM free-text output is untrusted for leakage.** Prompt instructions are not a compliance control. When tool invocations are logged, prefer enum/structured parameters over free text, or sanitize before the logger.
- **Never persist secrets to disk, even "temporarily"** -- test state files and scratch JSON included. Env or memory only; a crash before teardown leaves the credential behind on a shared runner.

---

## Testing

- **Wait on the source of truth, never timing proxies.** Poll the backend/database (`expect.poll()` or equivalent) until the expected state exists, then assert the UI reflects it. No fixed sleeps, no URL heuristics. Prefer database-state comparisons over DOM assertions for components that re-render while data streams.
- **Deterministic identifiers only.** No `Date.now()` / `Math.random()` in test data: it breaks seeded lookups, collides under parallelism, and changes prompt hashes so LLM caches miss in CI. Fixed, descriptive, per-test constants give each parallel test an isolated slice of seed data.
- **Extract shared helpers into per-domain util files** (`tests/utils/<domain>.ts`) when a >20-line block repeats across tests, setup obscures intent, or a file passes ~1500 lines. Type every helper parameter and return. Keep test-specific setup in the test itself.
- **Group related test data into structured objects**, not loose variables -- self-documenting, typo-proof, scales with fixtures.
- **Mock external/LLM APIs when the UI or isolation is under test; use real calls only when the generation itself is** (then require seeded caches for determinism). Always unroute/clean up in `finally`.
- **For LLM-backed logic**: unit-test the wrapper with a mocked model across safe/blocked/timeout/error paths (including metric emission), and separately maintain a labeled eval corpus with an accuracy threshold as its own suite.
- **Deterministic selection queries order by immutable natural columns**, not metadata timestamps, and use only columns the test schema exposes.
- **After migrations, sweep raw SQL in fixtures for the old schema** -- type generation updates itself; hardcoded SQL strings don't.
- **Multi-service E2E declares a health-check URL per service** so the harness polls readiness; health URLs are the guard against inter-service startup races.

Tighten test matchers so a test fails on anything other than the exact expected value; this is a state-space concern owned by `state-space-minimization`.
