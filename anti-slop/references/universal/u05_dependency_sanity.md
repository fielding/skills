First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: Dependency Sanity & Supply Chain

Goal: Judge whether the dependency set is sane, real, and reproducible. Vibe-coded projects
commonly import packages that don't exist, pile on redundant libraries, or ship no lockfile.

Inspect manifests (do NOT install). Adapt to the package manager from stack.md:
  cat package.json 2>/dev/null            # deps, devDeps, scripts
  cat requirements.txt pyproject.toml go.mod Cargo.toml 2>/dev/null
  rg -n "preinstall|postinstall|prepare" package.json
  rg -n "github:|git\+|file:|http://|https://" package.json   # unversioned/url deps

Checks:
1. **Hallucinated / nonexistent packages** — any dependency that isn't a real published
   package, or whose name is a near-miss of a popular one (typosquat / LLM invention).
   Verify suspicious ones: `npm view <pkg> version 2>&1 | head -1` (read-only registry query).
2. **Lockfile present and committed?** No lockfile = non-reproducible = a real tell.
3. **Bloat** — dependency count wildly disproportionate to the app (e.g. 60 deps for a
   to-do CLI), multiple libraries doing the same job (3 date libs, 2 HTTP clients).
4. **Phantom imports** — code imports modules not declared in the manifest (will break on
   clean install): cross-check a sample of imports against declared deps.
5. **Unused declared deps** — declared but never imported (cruft, not dangerous).
6. **Install-time scripts** — postinstall/preinstall that network or touch the filesystem.
7. **Direct git/url deps** — no integrity hash, can change under you.
8. If a CVE tool is trivially available read-only (`npm audit`, `pip-audit`), note critical/high
   in the auth/crypto/network path — but don't block on transitive noise.

Hard BLOCKER:
- A hallucinated/nonexistent dependency the code actually imports (won't build).
- No lockfile in a project presented as shippable.
- A postinstall script that exfiltrates or fetches+executes remote code.

Headline: dep count, lockfile yes/no, # hallucinated, # phantom imports.

Write findings to `.antislop/findings/u05_dependency_sanity.md`.
