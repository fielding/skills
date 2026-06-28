First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: TS — Test Reality (real tests or theater?)

Goal: Determine whether the tests actually verify the software's core behavior, or just exist
to make a coverage badge green. Theater tests are a top vibe-code tell: present, plentiful,
and meaningless.

Survey then (optionally) run:
  find . -name '*.test.ts' -o -name '*.test.tsx' -o -name '*.spec.ts' | grep -v node_modules | head -40
  rg -n "describe\(|it\(|test\(" --glob '*.test.*' --glob '*.spec.*' | wc -l
  rg -n "\.skip\(|\.todo\(|xit\(|xdescribe\(|it\.only|fdescribe" --glob '*.test.*' --glob '*.spec.*'
  rg -n "expect\(true\)|toBeTruthy\(\)\s*$|toBe\(true\)|expect\(1\)\.toBe\(1\)|assert\(true\)" --glob '*.test.*'
  npx jest --listTests 2>/dev/null | head -30
  # If fast and offline-safe, run a subset: npx jest --passWithNoTests <one dir> 2>&1 | tail -30

Assess each test file, not the count:
1. **Do tests assert anything meaningful?** Or `expect(true).toBe(true)`, snapshot-only,
   render-without-assert, `expect(fn).toBeDefined()`.
2. **Is everything mocked?** If the unit under test is fully mocked away, the test verifies the
   mock, not the code. Look for tests that mock the very function they claim to test.
3. **Skipped / todo / only** — suites silently disabled (`.skip`, `xit`, `it.todo`) or pinned
   to one test (`.only`) that hides the rest.
4. **Core-risk coverage** — does ANY real test exist for the project's actual critical logic
   (the things u02 said are the product's promise)? Map tests → core modules. Coverage % is
   irrelevant if it covers getters and config.
5. **Do they pass?** If you can run them cheaply and safely, do; report pass/fail. Tests that
   don't even run are worse than none (false signal).
6. **Fixtures** — real-ish data, or all `foo`/`bar`/empty objects that never exercise edges?

Hard BLOCKER:
- Zero real tests on the core/critical logic.
- Tests are theater (assert nothing / fully self-mocked) while advertised as a test suite.
- Test suite doesn't run / is broken but a "tests passing" claim is made.

Headline: # test files, # meaningful vs theater, core logic covered yes/no, suite runs/passes.

Write findings to `.antislop/findings/ts02_test_reality.md`.
