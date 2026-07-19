# Mutation mechanics (stage 4)

Per-tool run recipes for gate's mutation stage. Stage 4 in SKILL.md owns the
contract -- scope to the changed files, record caught / unviable / missed /
timeout, fix every survivor; this file holds how each tool actually runs and how
its vocabulary maps onto that record. Load it only when the mutation stage is
enabled.

## Shared mechanics

- **Scope to the diff.** Mutate only the changed *source* files from
  `git diff <base>...HEAD` -- never test files, generated code, or config.
  Whole-repo mutation is a different (and far longer) exercise than gating a
  branch.
- **Verdict mapping.** Every tool's vocabulary folds into gate's four buckets:
  **caught** (a test failed), **missed** (all tests passed -- a survivor to fix),
  **unviable** (the mutant didn't compile or was otherwise invalid -- not a gap),
  **timeout** (usually an infinite-loop mutant; a catch in spirit, but check the
  loop's stop-condition has a real test).
- **Recurring survivor patterns.** Error-path invariants survive when every
  boundary mock is infallible -- add a deliberately-failing impl to drive the
  `Err`/throw branch. Loop stop-conditions survive or hang under a `==` flip --
  drive the failing path AND wrap the loop in a timeout so a broken early-return
  trips the deadline.
- **Artifacts are run scratch.** The dirs these tools write (`reports/`,
  `.stryker-tmp/`, `mutants.out*/`, `html/`) are worktree scratch: never let them
  ride into a commit (the artifact rule in `fold-mechanics.md`).

## Stryker -- JavaScript / TypeScript

Tool: `@stryker-mutator/core`, run as `npx stryker run`.

**Preflight.** Stryker needs a test-runner plugin matching the repo's runner:
`@stryker-mutator/vitest-runner`, `@stryker-mutator/jest-runner` (mocha, karma,
jasmine, and tap runners also exist). If the repo has neither the deps nor a
`stryker.config.*`, install `@stryker-mutator/core` plus the plugin for the
detected runner as dev-deps rather than falling back to the generic
command-runner -- that fallback works anywhere but is several times slower and
cannot do per-test coverage analysis.

**Config.** Stryker reads `stryker.config.mjs|js|json` from the repo root. If the
repo has none, do not run the interactive `stryker init`; write a minimal config:

```js
// stryker.config.mjs
export default {
  testRunner: 'vitest',            // match the repo's runner
  reporters: ['clear-text', 'progress'],
  incremental: true,
};
```

For TypeScript repos, adding `@stryker-mutator/typescript-checker` and
`checkers: ['typescript']` makes Stryker classify compile-error mutants as
unviable instead of letting them surface as noisy runtime kills -- worth it on
anything beyond a tiny diff, at the cost of a tsc pass.

**Scope to the diff.** `--mutate` takes comma-separated globs; pass the changed
source files explicitly:

```bash
npx stryker run --mutate "src/parser.ts,src/lib/normalize.ts"
```

**Reruns inside the floor loop.** Keep `incremental` on (or pass
`--incremental`): Stryker caches results in `reports/stryker-incremental.json`
and re-tests only mutants whose code or covering tests changed, which makes the
fix-survivor -> rerun loop cheap.

**Reading the report.** `killed` -> caught; `survived` -> missed; `no coverage`
-> missed, and worse -- the mutated line is executed by no test at all, so fix
the coverage gap, not just an assertion; `timeout` -> timeout; compile/build
errors -> unviable. Ignore the mutation-score percentage and any
`thresholds.break` in the repo's config: gate's rule is fix every survivor on
the diff, not clear a score.

## cargo-mutants -- Rust

Tool: `cargo-mutants`, run as `cargo mutants`.

**Scope to the diff** with `--in-diff`, which limits mutants to code touched by
the patch:

```bash
git diff <base>...HEAD > /tmp/gate.diff && cargo mutants --in-diff /tmp/gate.diff
```

**Reading the output.** cargo-mutants' vocabulary *is* gate's record: caught /
missed / unviable / timeout, summarized at the end of the run and listed in
`mutants.out/` (`missed.txt` is the fix list). Unviable mutants are expected
noise, not gaps.

## mutmut -- Python

Tool: `mutmut`, run as `mutmut run`. Scope with `--paths-to-mutate` (or the
`[tool.mutmut] paths_to_mutate` key in `pyproject.toml`) pointed at the changed
source files; `mutmut results` lists survivors. Verdicts map directly: killed ->
caught, survived -> missed, suspicious/timeout -> timeout. The Python floor and
conventions pack are still being built out, so expect to adapt.
