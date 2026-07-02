First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: TS -- Runtime Safety (injection, boundaries, precision)

Goal: Catch the TS/JS-specific runtime hazards that vibe-coded apps leave open at the
boundaries -- injection sinks, unvalidated input, and number-precision bugs.

Scan (adapt to web/server/extension surfaces from stack.md):
  rg -n "dangerouslySetInnerHTML|innerHTML *=|outerHTML|eval\(|new Function\(|document\.write" --glob '!node_modules'
  rg -n "child_process|exec\(|execSync|spawn\(" --glob '!node_modules'
  rg -n "\$\{[^}]*\}" --glob '*.sql' ; rg -n "query\(`|raw\(`|\.query\([\"'][^\"']*\$\{" --glob '!node_modules'
  rg -n "JSON\.parse|\.json\(\)" --glob '!node_modules' | head -20
  rg -n "parseFloat|parseInt|Number\(|\.toFixed|\* *100|/ *100|Math\.(round|floor|ceil)" --glob '!node_modules' | head -30
  rg -n "zod|yup|joi|valibot|ajv|class-validator" package.json   # is any validation lib even present?

Checks:
1. **XSS / HTML injection** -- `dangerouslySetInnerHTML`, `innerHTML`, `document.write` fed by
   user/external data without sanitization. Worst on authenticated/sensitive screens.
2. **Code/command injection** -- `eval`, `new Function`, `child_process.exec` with interpolated
   input.
3. **SQL/NoSQL injection** -- string-interpolated queries instead of parameterized.
4. **Unvalidated external input** -- request bodies / query params / third-party API responses
   parsed and used without a schema (no zod/yup/etc. anywhere is itself a signal).
5. **Number precision** -- money/quantity math in JS `number` where it matters. `0.1 + 0.2`
   class bugs; large integer amounts beyond 2^53; `parseFloat` on currency; `* 100` cents
   math. Should use integer minor units / bigint / decimal lib.
6. **Unsafe deserialization / prototype pollution** -- spreading untrusted objects into config,
   `Object.assign` from request bodies, `__proto__` reachable.
7. **Client-trusted security** -- auth/authorization decided only on the client; secrets or
   admin flags in client-shipped code.

Hard BLOCKER:
- XSS reachable on an authenticated/sensitive screen.
- Command/SQL injection from user input.
- Money math in floating-point `number` on a path that moves real value.

Headline: injection sinks found, validation lib present?, precision-unsafe money math?

Write findings to `.antislop/findings/ts03_runtime_safety.md`.
