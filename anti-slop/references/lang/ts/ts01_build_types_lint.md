First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: TS — Build, Types & Lint (does it actually compile?)

Goal: Ground-truth whether the project builds and typechecks. "It runs on my machine" claims
collapse here. Running the toolchain read-only is permitted for THIS topic.

Permitted commands (read-only; do NOT run build/deploy that emits or installs):
  cat tsconfig*.json 2>/dev/null
  npx tsc --noEmit 2>&1 | tail -60          # the single most important signal
  npx eslint . --no-fix 2>&1 | tail -40     # only if eslint config exists
  rg -n "\"strict\"|strictNullChecks|noImplicitAny|skipLibCheck" tsconfig*.json

If `tsc`/`eslint` aren't installed and can't run without a network install, say so and base the
verdict on static reading — do NOT install.

Checks:
1. **Does `tsc --noEmit` pass?** Count and summarize errors. A project that doesn't typecheck
   is not "done," regardless of the README.
2. **Strictness** — is `strict` on? Or is the config loosened (`strict: false`,
   `noImplicitAny: false`, `skipLibCheck`) to make errors disappear rather than fixing them?
3. **Escape-hatch abuse** — count and locate:
     rg -n "\bas any\b|as unknown as|: any\b|@ts-ignore|@ts-expect-error|@ts-nocheck|eslint-disable"
   Especially around data boundaries, money/amounts, auth, and external inputs. Suppressed
   errors are hidden bugs the author chose not to face.
4. **Lint** — does it pass? Or are rules disabled wholesale / `eslint-disable` sprinkled to
   silence warnings?
5. **JS-only project**: skip type checks; still run eslint and flag `eval`/loose patterns.

Hard BLOCKER:
- `tsc --noEmit` fails (project does not compile).
- `strict` disabled or pervasive `as any`/`@ts-ignore` in security/money/auth code.

Headline: tsc pass/fail (+ error count), strict on/off, # escape hatches.

Write findings to `.antislop/findings/ts01_build_types_lint.md`.
