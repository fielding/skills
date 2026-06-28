# Cross-language / cross-system comparison axes

When teaching a new language, framework, or paradigm, anchor it to what the learner already knows. For each
axis, walk the four beats: **closest familiar equivalent → how it's similar → how it differs → where the
analogy breaks down.** Always name the break-down point explicitly — an unqualified analogy becomes a
future bug in the learner's mental model.

Draw on whichever axes are relevant; don't grind through all of them.

| Axis | What to contrast |
|---|---|
| Error handling | exceptions vs result/`Either` types vs return-value errors vs panics |
| Polymorphism | class inheritance vs composition vs traits/interfaces/protocols/typeclasses |
| Async model | promises vs async/await vs futures/tasks vs goroutines vs actors vs raw event loop |
| Nullability | `null` vs `Option`/`Maybe` vs nullable types vs sentinel values |
| Modules | packages vs namespaces vs modules vs imports; what's the unit of encapsulation |
| Mutability | mutable-by-default vs immutable-by-default; `const`/`final`/`let`/`val` semantics |
| Memory | manual vs GC vs ownership/borrowing/lifetimes vs ref-counting |
| Data modeling | enums vs tagged unions vs algebraic data types; pattern matching & destructuring |
| Types | inference, generics, constraints, structural vs nominal typing |
| Dependency wiring | DI containers vs service registration vs plain imports vs module boundaries |
| Testing | mocks vs fixtures vs fakes vs integration tests; unit boundaries |
| Failure timing | compile-time guarantees vs runtime failure; what the type system catches |

## Common traps to flag by origin

- **From a GC language → ownership (Rust):** "the borrow checker is just a linter" — no, it changes how you
  *structure* data, not just how you annotate it. Don't reach for `clone()`/`Rc` to silence it reflexively.
- **From exceptions → result types:** treating `?`/`unwrap` as "the same as throwing" — the control flow is
  explicit and local, not a stack-unwinding teleport.
- **From threads → async:** assuming `await` yields the CPU like a thread switch — it yields *cooperatively*;
  a blocking call inside an async fn stalls the whole executor.
- **From dynamic → static typing:** expecting runtime duck typing; the compiler wants the shape up front.
- **From classes → traits/interfaces:** modeling "is-a" hierarchies when the idiom is "can-do" capabilities.

Show side-by-side snippets in the familiar language and the new one when the difference is mechanical. The
goal is a correct mental model, not a syntax cheat-sheet — be explicit about what should *not* be
translated literally.
