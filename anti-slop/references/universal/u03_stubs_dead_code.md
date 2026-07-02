First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: Stubs, Placeholders & Dead Code (measures hollowness)

Goal: Measure how much of the codebase is real vs. scaffolding never filled in. Vibe-coded
projects are wide and shallow -- many files, many function signatures, little working body.

Scan (adapt globs to the detected languages):
  rg -n "TODO|FIXME|XXX|HACK|placeholder|stub|not implemented|unimplemented" --stats
  rg -n "throw new Error\(['\"]not implemented|NotImplementedError|todo!\(\)|panic!\(\"todo|raise NotImplementedError|pass *# *TODO"
  rg -n "return null;?\s*//|return \{\};?\s*//|return \[\];?\s*//|// *placeholder|// *mock|// *fake"
  rg -n "console\.log\(['\"](test|debug|here|asdf|xxx)" 

Look for the shapes of fake completeness:
1. **Empty/placeholder bodies** -- functions that only `return null/{}/[]/true`, log, or
   re-throw, with a name implying they should do real work.
2. **Unreachable / unwired code** -- exported functions never imported; routes/handlers
   defined but not registered; components never rendered; dead branches.
3. **Commented-out blocks** -- large swaths of commented code (abandoned attempts).
4. **Duplicate-but-divergent files** -- `foo.ts`, `foo2.ts`, `foo.old.ts`, `foo.new.ts`,
   `foo.backup.ts` (session churn left in the tree).
5. **Generated-and-never-touched** -- boilerplate from a template/generator with default
   names ("my-app", "TODO: describe", example handlers) still in place.
6. **Magic placeholder values** -- `"https://example.com"`, `"YOUR_API_KEY_HERE"`, `foo@bar.com`,
   lorem ipsum in shipped paths.

Quantify the hollowness: count of stub/placeholder markers, and roughly what fraction of the
core modules have real bodies vs. are scaffolding. That number is the headline.

Hard BLOCKER:
- A core module/feature is a stub (cross-check u02's claim list).
- Critical path returns a hardcoded/placeholder value instead of computing the real one.

Write findings to `.antislop/findings/u03_stubs_dead_code.md`.
