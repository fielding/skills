First read prompts/shared_rules.md and prompts/findings_schema.md.

# Topic: Inventory & Stack Detection (run first -- context for everything else)

Goal: Map the repo and detect the stack so every later topic starts with accurate context.
Do not make quality judgments yet -- only map. This topic is NOT scored.

Detect, from files actually present (not the README's claims):
1. **Languages** -- by file extension counts and manifest files: package.json (ts/js),
   pyproject.toml/requirements.txt (py), go.mod (go), Cargo.toml (rust), etc.
2. **Package manager(s)** -- lockfile present? npm/pnpm/yarn/bun, pip/poetry/uv, cargo. Note
   if NO lockfile exists.
3. **Frameworks & runtime** -- Next/React/Vue/Express/FastAPI/Django/Axum/etc.
4. **App surfaces** -- web app, API/server, CLI, mobile, browser extension, library,
   serverless functions, smart contracts.
5. **Domain guess** -- what kind of product is this? crypto-wallet, web-api, saas, cli-tool,
   ml-app, game, content-site, library, unknown. Base it on dependencies + directory names +
   entrypoints, not marketing copy.
6. **Entrypoints** -- main/index files, bin scripts, server boot, build/start scripts.
7. **Manifest scripts** -- flag any preinstall/postinstall/prepare/deploy/`rm -rf`/curl/wget.
8. **Rough size** -- file count, LOC ballpark (excluding deps/lockfiles/generated).

Commands (adapt to what exists):
  ls -la; git log --oneline | head -20; git log --oneline | wc -l
  cat package.json pyproject.toml go.mod Cargo.toml 2>/dev/null
  find . -maxdepth 3 -type f -not -path '*/node_modules/*' -not -path '*/.git/*' | head -200
  find . -name '*.lock' -o -name '*-lock.json' -o -name '*.lockb' 2>/dev/null | grep -v node_modules

Write `.antislop/evidence/stack.md` with a clear declaration block the other agents read:
```
languages: <list>
package_managers: <list, or "NONE -- no lockfile">
frameworks: <list>
surfaces: <list>
domain_guess: <one of the labels above>
toolchain_for_language_pack: <ts | py | go | rust | none>
notes: <anything an auditor must know>
```

Then write your topic file to `.antislop/findings/u01_inventory_stack.md`. Verdict here is
informational: PASS unless the repo is unmappable (then INCONCLUSIVE).
