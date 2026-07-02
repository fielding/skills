---
name: rust-conventions
description: >-
  Battle-tested Rust conventions for writing and reviewing Rust. Covers
  error modeling (per-module errors, associated types over jokers,
  Infallible for unreachable variants, .expect over .unwrap),
  fail-loud-with-context, redacted Debug for PII, role-named interfaces,
  one-lock-for-joint-invariants, comment-only-the-why, walking the error
  source chain, no #[inline], internal-only todo!() seams, and the clippy
  restriction-lint gotchas that recur. Cross-references
  state-space-minimization for the language-agnostic state-shrinking
  principles. Use when writing or reviewing Rust code (*.rs, Cargo.toml)
  in a project that has not already declared its own conventions.
allowed-tools: Read, Grep, Glob, Bash, Skill
---

# Rust Conventions

A baseline of Rust conventions distilled from high-bar reviews. Two layers:

1. **General principles** (any language, but stated here in their Rust expression). The `typescript-conventions` pack restates the same ideas in TypeScript's idiom; a Python pack is planned.
2. **Rust idioms** (the specific mechanism the language gives you).

Defer to a project's own conventions where it has declared them; use these to fill the gaps.

> The state-shrinking principles, parse-don't-validate, drop speculative tolerance, validate at the boundary, no dead or speculative code, are owned by the **`state-space-minimization`** skill. This skill does not restate them. Invoke `state-space-minimization` alongside this one when writing or reviewing; the two compose. Where a convention below is a Rust mechanism *for* an SSM principle, it says so and points back.

---

## General principles (Rust expression)

These hold in any language. They are stated here the way Rust lets you express them.

### Fail loud, with context

A boundary failure should surface, not be swallowed. Do not invent recovery (retry-with-backoff, quarantine, fallback values) on the first pass; let the failure propagate and let the layer that owns the recovery policy decide. In a worker that pulls from a broker: on a processing failure, do not ack, so the broker redelivers and the dead-letter path catches it. The simplest correct handling is "stop and report," and it is usually the right first iteration.

A loud failure is only useful if it says *what* failed. See "Walk the error source chain" below for the reporting side.

### Redact PII and secrets in Debug and logs

A value holding email content, message bodies, user-derived text, or a secret must not be able to leak through a stray `{:?}` in a log line or a panic message.

- Hand-write `Debug` for such types. Keep the correlation IDs and presence flags; drop the payload.
- Wrap secrets in a type whose `Debug`/`Display` cannot print the inner value (see "Secret handling").
- Reserve redaction for genuine secrets and PII. A short-lived opaque handle (an ack lease, a surrogate id) is not a secret; redacting it costs debuggability for zero security gain. A hand-rolled `Debug` is a signal that something is being hidden or reshaped, so if every field is plain metadata, derive it and let it stay honest.

```rust
// Hand-rolled Debug that keeps the shape, drops the content
impl fmt::Debug for InboundMessage {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("InboundMessage")
            .field("id", &self.id)
            .field("body_len", &self.body.len()) // length, not body
            .finish()
    }
}
```

### Role-named, single-word interfaces

Name a trait for the role it plays, not the mechanism behind it: `Inbox`, `Sender`, `Database`, `Worker`, not `RabbitMqConsumer` or `PostgresGateway`. The name is the contract; the implementation name carries the mechanism. This keeps call sites reading as intent and lets you swap the implementation without renaming the seam.

### One lock for joint invariants

State that must change together belongs under one lock. A counter and the queue it indexes, a flag and the buffer it guards: split them across two locks and a reader can observe the pair half-updated. If two pieces of state share an invariant, they share a lock.

### Comment only the why

Terse code over narration. Drop any comment that restates what the next line plainly does. Keep the non-obvious *why*: an invariant, a subtle ordering, a redaction rationale, a boundary contract, the result of an empirical probe. Doc comments on public items are required (and often lint-enforced), but a one-line doc that adds information beats a paragraph that just re-spells the signature, and a trait-impl method inherits the trait's docs. Excess comments are review noise; a high-bar reviewer reads terse.

### Walk the error source chain at the entry point

Per-module errors carry their detail behind `#[source]` (see "Errors"). If `main` logs only the top-level `Display`, every underlying cause is invisible and the log cannot name the failing dependency. The reporter at the entry point must iterate `.source()` and log each cause.

```rust
fn report(err: &(dyn std::error::Error + 'static)) {
    eprintln!("error: {err}");
    let mut source = err.source();
    while let Some(cause) = source {
        eprintln!("  caused by: {cause}");
        source = cause.source();
    }
}
```

A log that prints only the outermost error has thrown away the reason it exists.

---

## Errors

The heart of these conventions. Error modeling is where Rust gives you the most leverage and where reviews concentrate.

### Per-module `Error`, no crate-wide sum

Each module owns an error type named `Error`. A function that composes several modules declares its own local error at the use site that wraps the ones it calls. There is no single `crate::Error` that every failure funnels into.

A crate-wide sum error widens the failure surface of every function to the union of everything the crate can fail at: a caller can no longer tell, from the type, what a given call can actually do wrong. Per-module errors keep each function's failure set honest. This is a state-space concern; see `state-space-minimization`.

### Explicit conversion: `.map_err` + `#[source]`, never `#[from]`

Convert errors explicitly at the call site with `.map_err(...)`, and attach the cause with `#[source]`. Do not derive `#[from]`.

`#[from]` installs an implicit `?`-conversion that fires in *any* caller's scope, so an unrelated function silently gains the ability to absorb that error into its own type, widening its failure surface without anyone deciding to. `.map_err` forces the conversion to be written where it happens, which is where the decision belongs.

`Display` for an error variant must **omit** the source's content (no `{0}` printing the wrapped error). A chain-walking reporter already prints each cause; if `Display` also embeds the source, every cause prints twice.

```rust
#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("failed to load config")] // no {0}; the source is walked, not inlined
    LoadConfig {
        #[source]
        source: ConfigError,
    },
}

let cfg = load().map_err(|source| Error::LoadConfig { source })?;
```

### Associated types over jokers; `Infallible` for unreachable variants

When a trait's value or error differs per implementation, an ack handle, a transport error, a lease, use an **associated type**, not a shared `String` newtype and not `Box<dyn Error>`. A `Box<dyn Error>` or stringly error is a joker: it erases the type and lets any error masquerade as any other.

For a case an implementation genuinely cannot reach, use `core::convert::Infallible` as the associated error type. The unreachable variant then does not exist structurally; nobody has to write or test a branch that cannot happen.

```rust
trait Inbox {
    type Lease;          // the ack handle, per implementation
    type TransportError; // each transport's own error
    fn next(&mut self) -> Result<InboxItem<Self::Lease>, Self::TransportError>;
}

// An in-memory implementation that cannot fail on transport:
impl Inbox for MemoryInbox {
    type Lease = MemoryLease;
    type TransportError = core::convert::Infallible;
    // ...
}
```

### `.expect`, never `.unwrap`

Use `.expect("the invariant, and what a violation means")`, never bare `.unwrap()`. Many high-bar workspaces ban `.unwrap()` via clippy outright.

`.expect` hides nothing that `.unwrap` would show: both print the inner error's `Debug` through the same `unwrap_failed` path, so you lose no detail. `.expect` only *adds* the human reason. The standard counter-argument, "but `expect` will hide the underlying error," is wrong; the reproducer is a poisoned mutex, where `.lock().unwrap()` and `.lock().expect("...")` both print `PoisonError { .. }`. Write the reason as the invariant you are asserting.

### `todo!()` seams: internal only, never on a reachable command path

`todo!()` is fine for an *internal* seam someone will fill in. It must never sit on a path a user can reach: a `todo!()` on a mounted command's default path panics the binary in the user's hands. Make user-reachable stubs fail gracefully, return an `Err(Unconfigured)`-style variant, rather than panic.

Most restriction-lint configs deny `clippy::todo`, so every `todo!()` needs `#[expect(clippy::todo, reason = "...")]`.

---

## Secret handling

- Wrap secrets in a redacting wrapper type (e.g. `secrecy::SecretString`, or `SecretBox<T>`). Its whole point is to make accidental logging through `Debug`/`Display` impossible.
- Do not call `expose_secret()` until the last possible moment, the HTTP header, the connection string, the subprocess arg. Keep the value wrapped through every intermediate signature, struct field, and channel message.
- Never unwrap a secret to a plain `String` early and pass it around; that defeats the wrapper, because the bare `String` can now land in a `tracing` event, an error, or a panic.

```rust
use secrecy::ExposeSecret;

let resp = client
    .post(url)
    .header("Authorization", format!("Bearer {}", self.api_key.expose_secret()))
    .send()
    .await?;
```

For an operator-facing command, read credentials straight from the environment (`std::env::var("...")`) and let secret *placement* (a secret manager, CI secrets) live outside the binary. The binary consumes the environment; it does not know where the value came from.

---

## No `#[inline]` attributes

Do not annotate functions with `#[inline]`. Let the compiler decide; it is better at this than a hand-placed hint, and a stray `#[inline]` is noise that drifts out of any real justification. Strip any that creep in. (If a workspace genuinely needs inlining hints it will say so; absent that, none.)

---

## Logging levels

Use `tracing`. Pick the level by whether the reader must act:

- **`error`** -- requires action. Must carry actionable context: what failed, why, what to do. If there is nothing to do, it is not an error.
- **`info`** -- system behavior, including expected-and-handled error conditions.
- **`debug`** -- detail not wanted in production logs.
- **Avoid `warn`.** It is ambiguous about whether action is needed. Either it matters (`error`) or it does not (`info`).

Never log user content (prompts, message bodies, responses, file contents, anything PII-derived) at a level reachable in production. When logging an error that touches user data, log the error type or code, not the data. See "Redact PII and secrets" above; this is the logging face of the same rule.

---

## Imports

- All `use` statements at the top of the file, after module attributes and the module doc comment. No inline `use` inside functions (except where conditional compilation forces it, e.g. inside a `#[cfg(test)]` module).
- Group, separated by blank lines: standard library, then external crates, then crate-internal (`crate::`, `super::`, `self::`).

```rust
use std::collections::HashMap;
use std::sync::Arc;

use serde::{Deserialize, Serialize};

use crate::config::Config;
```

---

## Dependencies

Add crates with `cargo add <crate>` (and `--features <f>` for features), not by hand-editing `Cargo.toml`. `cargo add` picks the latest compatible version, writes canonical formatting, and keeps `Cargo.lock` consistent; hand edits routinely produce stale versions and merge churn.

---

## Testing

Place unit tests in a **sibling `<module>_test.rs` file**, not inline at the bottom of the source. Include it with `#[path]`.

```rust
// in bar.rs
pub fn add(a: i32, b: i32) -> i32 { a + b }

#[cfg(test)]
#[path = "bar_test.rs"]
mod tests;
```

```rust
// in bar_test.rs
use super::*;

#[test]
fn adds() {
    assert_eq!(add(2, 2), 4);
}
```

The source file stays focused on the implementation, the tests can grow without bloating it, and `grep` for `_test.rs` finds every test file uniformly.

Integration tests live in `tests/` at the crate root and exercise the public API as an external consumer would. Each file there compiles as its own crate, so put shared helpers behind a common module (`tests/common/mod.rs`).

Tighten test matchers so a test fails on anything other than the exact expected value; this is a state-space concern owned by `state-space-minimization`.

---

## Clippy and the restriction-lint gotchas

Run clippy with warnings as errors (`cargo clippy -- -D warnings`), and prefer a project alias (`cargo clippy-all`, `just lint`) if one exists, since it encodes the full lint surface (all features, all targets, workspace-wide).

Projects that turn on the clippy **restriction** group hit a recurring set of lints whose fixes are not obvious. Each one below otherwise costs a build round-trip:

- **`shadow_unrelated`** -- do not rebind a name to an unrelated value. When destructuring (e.g. an `into_parts()`), give the bindings fresh names rather than reusing the field names already in scope.
- **`renamed_function_params`** -- a trait-impl method must keep the trait's parameter names. To discard an unused stub parameter, write `let _: &T = param;`, not `_param` and not an untyped `let _`.
- **`missing_trait_methods`** -- derive errors with `#[derive(thiserror::Error)]`; do not hand-roll `impl std::error::Error`. This applies to test-only error types too.
- **`empty_structs_with_brackets`** -- write `struct X;`, not `struct X {}`.
- **`unused_trait_names`** -- when you import a trait only for its methods, write `use Trait as _;`.
- **`missing_const_for_fn`** -- a trivial-body function (a stub constructor) must be `const fn`. But a `const fn` cannot move a generic field with a destructor out of `self`, so a `new` constructor can be `const` while an `into_parts` that destructures `self` cannot.
- **Intra-doc-link gotcha** -- module-level `//!` intra-doc links to imported items do not resolve. Use a plain code span or an explicit path instead.

For uncertain library behavior, write an **empirical probe** and capture the result in a comment rather than guessing; the comment is exactly the kind of "why" worth keeping.
