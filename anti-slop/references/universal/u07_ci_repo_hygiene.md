First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: CI & Repo Hygiene

Goal: Distinguish a maintained project from a one-shot generation dressed up to look
maintained. The signals are cheap to read and hard to fake well.

Inspect:
  ls -la .github/workflows .gitlab-ci.yml .circleci 2>/dev/null
  cat .github/workflows/*.yml 2>/dev/null | head -120
  git log --oneline | head -30
  git log --format='%an' | sort | uniq -c
  git log --format='%s' | head -30
  cat .gitignore 2>/dev/null
  ls -la | rg "node_modules|dist|build|\.env|\.DS_Store"   # tracked junk?

Checks:
1. **Real CI?** -- is there a pipeline, and does it actually do something (install + build +
   test + lint), or is it a hello-world / `echo passing` placeholder? Does it run on PRs?
2. **CI honesty** -- does the "build passing" badge correspond to a job that truly builds and
   tests, or to a no-op? Does CI `continue-on-error` past failures?
3. **Commit history shape** -- one giant "Initial commit" with the whole app is a strong
   vibe-dump tell. Look for organic, incremental history vs. a single paste.
4. **Authors / co-author tells** -- generated-by markers, single author, no review trail.
5. **.gitignore sanity** -- present and covering deps/build/env? Or is `node_modules`/`dist`/
   `.env` committed?
6. **Tracked junk** -- build artifacts, `.DS_Store`, editor files, large binaries in the tree.
7. **Branch/PR discipline** -- any sign of review (PRs, tags, releases) vs. direct-to-main dump.

This topic rarely produces BLOCKERs on its own, but a no-op CI advertised as real coverage is
a confident-lie -- flag it HIGH and feed the headline to the verdict.

Headline: real CI yes/no, # commits, single-dump yes/no, tracked junk yes/no.

Write findings to `.antislop/findings/u07_ci_repo_hygiene.md`.
