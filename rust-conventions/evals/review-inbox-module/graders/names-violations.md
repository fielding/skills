---
type: llm
focus: last_message
weight: 2
---

The crate has six planted convention violations. The review must name them with enough
location detail that the author could find each one.

1. `.unwrap()` on `Mutex::lock()` in `Inbox::push`, `Inbox::take` and `Inbox::processed`
   (and `.unwrap()` in the test). Convention: `.expect("<invariant>")`, never bare `.unwrap()`.
2. Joker error types: `Box<dyn std::error::Error>` as the return error of the `RabbitMqConsumer`
   trait methods and the `Other(Box<dyn Error>)` variant of `inbox::Error` (the stringly
   `lease: String` ack handle is part of the same problem). Convention: associated types per
   implementation (`type TransportError;`, `type Lease;`), `Infallible` for unreachable cases.
3. `#[from]` on the `Transport` and `Decode` variants, with `{0}` printing the wrapped source
   in the `#[error(...)]` Display string. Convention: `#[source]` field, `.map_err(|source|
   Error::Variant { source })` at the call site, Display that omits the cause.
4. `#[inline]` on `Inbox::new`. Convention: no `#[inline]` attributes at all.
5. `#[derive(Debug)]` on `InboundMessage`, which holds the full user `body` and a bearer
   `reply_token`, then logged whole via `tracing::warn!(?msg, ...)`. Convention: hand-written
   `Debug` keeping id/length and dropping the payload, a redacting wrapper for the token, and
   never log user content; also `warn` is a level the conventions avoid.
6. `todo!()` on `Command::Replay` in `cli::run`, a user-reachable command path. Convention:
   `todo!()` is for internal seams only; a reachable stub returns an `Err(Unconfigured)`-style
   variant instead of panicking.

PASS if the review identifies at least FOUR of the six, each with the file or function it
lives in and a fix that points in the convention's direction.

FAIL if three or fewer are identified, or if it fabricates code that is not in the fixture
(quoting functions, files or lines that do not exist). Additional legitimate findings beyond
the six (naming, test layout, style) are fine and must not cause a FAIL. Praising the derived
Debug, the `#[from]` conversions, or the `#[inline]` is a FAIL regardless of count.
