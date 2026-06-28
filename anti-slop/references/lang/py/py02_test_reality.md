First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: Python — Test Reality (real tests or theater?)

Goal: Determine whether the tests verify the software's actual behavior, or just exist to look
tested. Theater tests are a top vibe-code tell.

Survey then (optionally) run:
  git ls-files 'test_*.py' '*_test.py' 'tests/**.py' | head -40
  rg -n "def test_|class Test" --glob '*test*.py' | wc -l
  rg -n "@pytest\.mark\.skip|@pytest\.mark\.xfail|@unittest\.skip|pytest\.skip\(|return *# *skip" --glob '*test*.py'
  rg -n "assert True|assert 1 *== *1|assert .* is not None *$|\.assert_called|pass *# *TODO" --glob '*test*.py'
  (pytest --collect-only -q 2>&1 | tail -30)
  # If cheap and offline-safe: pytest -q <one dir> 2>&1 | tail -30

Assess each test file, not the count:
1. **Do tests assert meaningful behavior?** Or just `assert True`, `assert x is not None`,
   `assert resp.status_code == 200` with no body check, or import-only "smoke" tests.
2. **Is everything mocked?** A test that mocks the function under test, or patches so much that
   only the mock is exercised, verifies nothing. Watch for `MagicMock` standing in for the
   actual logic and assertions only on `.called`.
3. **Skipped / xfail** — suites silently disabled with `@pytest.mark.skip`/`xfail`, or
   conditionally skipped so they never run in practice.
4. **Core-risk coverage** — does ANY real test exercise the project's actual critical logic
   (the things u02 said are the product's promise)? Map tests → core modules.
5. **Do they pass?** If runnable cheaply and safely, run and report pass/fail. Tests that don't
   even collect/run are a false signal worse than none.
6. **Fixtures** — realistic data, or all empty dicts / `"foo"` that never hit edges?

Hard BLOCKER:
- Zero real tests on the core/critical logic.
- Tests are theater (assert nothing / fully self-mocked) while advertised as a suite.
- Suite doesn't collect/run but a "tests passing" claim is made.

Headline: # test files, # meaningful vs theater, core covered yes/no, suite runs/passes.

Write findings to `.antislop/findings/py02_test_reality.md`.
