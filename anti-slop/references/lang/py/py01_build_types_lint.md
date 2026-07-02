First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: Python -- Imports, Types & Lint (does it actually run?)

Goal: Ground-truth whether the code imports cleanly, type-checks, and lints. Python's late
binding hides broken code that never executed -- a vibe demo can import a module that doesn't
exist on any path the author didn't click. Running read-only tooling for THIS topic is allowed.

Permitted commands (read-only; do NOT install packages or run app/deploy code):
  cat pyproject.toml setup.cfg setup.py tox.ini 2>/dev/null
  python -m py_compile $(git ls-files '*.py' | head -200) 2>&1 | tail -40   # syntax-level "does it parse"
  python -c "import ast,sys; [ast.parse(open(f).read(), f) for f in sys.argv[1:]]" $(git ls-files '*.py') 2>&1 | tail -20
  (mypy . 2>&1 || pyright 2>&1) | tail -50        # only if a type checker is configured/installed
  (ruff check . 2>&1 || flake8 2>&1 || pylint -E $(git ls-files '*.py') 2>&1) | tail -40

If a tool isn't installed and would require a network install, say so and fall back to static
reading -- do NOT install.

Checks:
1. **Does it parse / compile?** `py_compile` over all tracked `.py`. Any SyntaxError is a hard fail.
2. **Do imports resolve?** Spot-check that imported modules are declared deps or stdlib/local --
   `import` of a package not in requirements/pyproject means it breaks on a clean install
   (cross-reference u05). Look for imports of sibling modules that don't exist.
3. **Type checking** -- is mypy/pyright configured and clean? Or absent entirely (no hints at
   all is a signal), or silenced with blanket `# type: ignore` / `Any` everywhere?
4. **Escape-hatch / suppression abuse** -- count and locate:
     rg -n "# *type: *ignore|# *noqa|# *pylint: *disable|: *Any\b|cast\(" --glob '*.py'
   Especially around money, auth, and external-data boundaries.
5. **Lint** -- does ruff/flake8/pylint pass, or is it absent / blanket-disabled?
6. **Packaging sanity** -- is there a real entrypoint / installable package, or a loose pile of
   scripts with no `__init__`/`pyproject` and implicit sys.path assumptions?

Hard BLOCKER:
- Any file fails to parse/compile.
- Imports a module that isn't declared and isn't available (won't run on a clean checkout).
- Type checker configured but failing and silenced, in security/money/auth code.

Headline: compiles yes/no, type-checker present+clean?, # suppressions, lint pass/fail.

Write findings to `.antislop/findings/py01_build_types_lint.md`.
