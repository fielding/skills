# Language Pack Selection

The orchestrator reads `.antislop/evidence/stack.md` (from `u01_inventory_stack`) and picks a
language pack from `toolchain_for_language_pack`. Mapping:

| Signal (files present) | Pack | Status |
|---|---|---|
| package.json + .ts/.tsx | `lang/ts` | **implemented** |
| package.json + .js/.jsx only | `lang/ts` (JS subset -- skip type checks) | **implemented** |
| pyproject.toml / requirements.txt / setup.py | `lang/py` | **implemented** |
| go.mod | `lang/go` | stub -- not built |
| Cargo.toml | `lang/rust` | stub -- not built |
| none of the above | none | run universal-only |

Rules:
- **Monorepo / polyglot**: if multiple toolchains are present, run each implemented pack and
  label findings by sub-project. Prefer the pack covering the security-critical surface.
- **Unbuilt pack matched**: do NOT fabricate language-specific findings. Run universal-only,
  and in the verdict state plainly: "language pack for <X> not yet implemented -- toolchain
  checks (build/typecheck/lint/test) were NOT run; confidence is reduced." This lowers
  confidence, not the score (the synthesis renormalizes weights over the topics that ran).
- Adding a pack later = drop a `lang/<name>/` folder with the same three-topic shape
  (build/types/lint · test-reality · runtime-safety) and add a row above. The engine and
  verdict format are unchanged.

Each language pack answers the same questions, with that language's tools:
1. Does it build / typecheck / lint cleanly?  (escape-hatch abuse: `as any`/`@ts-ignore`,
   `# type: ignore`/bare `except`, ignored `_ = err`, `.unwrap()` spam)
2. Are the tests real or theater?  (assert nothing / skipped / all-mocked / no core coverage)
3. Are runtime boundaries safe?  (injection sinks, unvalidated input, precision/overflow)
