First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: Error Handling & Input Validation

Goal: Find out whether the code survives anything but the happy path. Vibe-coded software
demos beautifully and falls over on the first bad input, empty result, or network error --
because failure paths were never written.

Scan (adapt to languages):
  rg -n "catch *\([^)]*\) *\{\s*\}|catch *\{\s*\}|except: *pass|except Exception: *pass|_ = err|_ , _ =" --glob '!node_modules'
  rg -n "\.catch\(\(\) *=> *\{\}\)|\.catch\(console\.(log|error)\)" --glob '!node_modules'
  rg -n "JSON\.parse|\.json\(\)|parseInt|parseFloat|Number\(|int\(|float\(" --glob '!node_modules' | head -30
  rg -n "req\.body|req\.query|req\.params|request\.|searchParams\.get|os\.environ\[" --glob '!node_modules' | head -30

Checks:
1. **Swallowed errors** -- empty catch blocks, `except: pass`, `.catch(() => {})`, ignored
   error returns (`_ = err`), errors logged-and-continued where they shouldn't be.
2. **Unhandled async** -- promises without catch, `await` with no try, fire-and-forget that
   can reject; missing error boundaries.
3. **Happy-path-only** -- functions that assume success: no handling for empty/null results,
   404s, timeouts, rejected payments, failed writes.
4. **Missing input validation at boundaries** -- request bodies, query params, env vars,
   external API responses, file contents, user input used without validation/parsing
   (no schema/zod/pydantic/manual checks). Trust placed directly in untrusted input.
5. **Crash-on-malformed** -- `JSON.parse`/`parseInt`/array access on data that could be
   malformed, with no guard.
6. **Error messages that lie or leak** -- generic "something went wrong" masking real failures,
   or raw stack traces / internal details returned to callers.
7. **No timeouts / retries** on network calls that need them.

Hard BLOCKER:
- A critical operation (payment, write, auth, money movement) silently swallows failure and
  reports success.
- Core endpoints crash on trivially malformed input (no validation anywhere).

Headline: # swallowed errors, validation present/absent at boundaries, happy-path-only?

Write findings to `.antislop/findings/u09_error_handling.md`.
