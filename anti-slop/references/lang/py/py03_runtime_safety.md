First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: Python -- Runtime Safety (injection, boundaries, deserialization)

Goal: Catch the Python-specific runtime hazards vibe-coded apps leave open -- injection,
unsafe deserialization, and unvalidated boundaries.

Scan (adapt to web/API/CLI/data surfaces from stack.md):
  rg -n "eval\(|exec\(|os\.system\(|os\.popen\(|subprocess\.(call|run|Popen).*shell *= *True" --glob '*.py'
  rg -n "pickle\.loads?\(|yaml\.load\((?!.*Loader)|marshal\.loads|dill\.load|__reduce__" --glob '*.py'
  rg -n "\.execute\(.*%|\.execute\(.*\+|\.execute\(f[\"']|cursor\.execute\(.*format|text\(f[\"']" --glob '*.py'   # SQL string building
  rg -n "render_template_string|Template\(|jinja2\.Template|autoescape *= *False|Markup\(|\|safe" --glob '*.py' --glob '*.html'
  rg -n "request\.(args|form|json|data|values)|flask\.request|@app\.route|@router\.(get|post)" --glob '*.py' | head -30
  rg -n "pydantic|marshmallow|cerberus|voluptuous|schema|@validator" --glob '*.py' pyproject.toml requirements.txt
  rg -n "open\(.*request|os\.path\.join\(.*request|\.\./|send_file\(.*request" --glob '*.py'   # path traversal
  rg -n "requests\.(get|post)\((?!.*timeout)|httpx\.(get|post)\((?!.*timeout)" --glob '*.py'   # no timeout

Checks:
1. **Code/command injection** -- `eval`/`exec`/`os.system`/`subprocess(..., shell=True)` with
   interpolated input.
2. **Unsafe deserialization** -- `pickle.loads`/`yaml.load` (without `SafeLoader`)/`marshal` on
   data that could be attacker-controlled. Classic RCE vector.
3. **SQL injection** -- `%`/`+`/f-string/`.format` interpolation into `execute()`/`text()`
   instead of parameterized queries or the ORM.
4. **Template / SSTI & XSS** -- `render_template_string` with user input, `autoescape=False`,
   `|safe`, `Markup()` on untrusted data.
5. **Unvalidated external input** -- Flask/FastAPI/Django request data parsed and used without a
   schema (pydantic/marshmallow). FastAPI's typed models help; raw `request.json` does not.
   No validation library present anywhere is itself a signal.
6. **Path traversal** -- user-controlled paths into `open`/`send_file`/`os.path.join`.
7. **`assert` for validation** -- asserts enforcing security/auth invariants are stripped under
   `python -O`; they must not be the only guard.
8. **Missing timeouts** on outbound HTTP; **debug mode** (`app.run(debug=True)`, `DEBUG=True`)
   shipped on.
9. **Secrets via config** vs inlined (overlaps u04).

Hard BLOCKER:
- Command/SQL injection or `eval`/`exec` from user input.
- `pickle`/`yaml.load`/`marshal` on attacker-controllable data.
- Auth/security invariant enforced only by `assert`.
- Flask/Django debug mode on in a "production" path.

Headline: injection sinks, unsafe deserialization?, validation lib present?, debug-on?

Write findings to `.antislop/findings/py03_runtime_safety.md`.
