First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: Docs vs Reality (the #1 slop signal)

Goal: Find the gap between what the project *claims* and what the code *does*. Confident
documentation describing behavior that doesn't exist is the single strongest tell of
vibe-coded / LLM-generated software. Treat every claim as a hypothesis to verify against code.

Gather the claims:
  cat README.md 2>/dev/null
  find . -iname '*.md' -not -path '*/node_modules/*' -not -path '*/.antislop/*' | head -40
  rg -n "TODO|FIXME|coming soon|not yet|planned|roadmap" README.md docs/ 2>/dev/null

For each significant claim in the README / docs / landing copy, classify it:
1. **Verified** -- there is code that plainly implements it (cite file:line).
2. **Stub** -- there's a function/route/page named for it, but it's empty, returns a
   placeholder, throws "not implemented", or is never wired up.
3. **Absent** -- no code implements it at all.
4. **Contradicted** -- code does the opposite of, or materially differs from, the claim.

Check specifically:
- "Features" / bullet lists -- does each one map to real, reachable code?
- Setup/usage instructions -- do the referenced commands, scripts, env vars, files exist?
- Code comments and docstrings -- do they describe what the function actually does, or an
  intended version? (`// validates and persists the user` over a function that only logs.)
- Architecture/diagram docs -- do the named modules/services exist?
- Badges (build passing, coverage %, "production ready") -- are they real or decorative?
- Screenshots/demos of features -- backed by code?

Hard BLOCKER:
- A core advertised feature is a stub or absent (the product's main promise isn't real).
- README presents the project as production-ready / shipped while core paths are unimplemented.

Quantify: of N headline claims, how many Verified / Stub / Absent / Contradicted. That ratio
is the headline for this topic.

Write findings to `.antislop/findings/u02_docs_vs_reality.md`.
