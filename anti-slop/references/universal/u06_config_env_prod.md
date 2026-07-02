First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: Config, Env Separation & Production Readiness

Goal: Judge whether this could actually run somewhere other than the author's laptop. Vibe
demos hardcode everything to localhost and call it done.

Scan:
  rg -n "localhost|127\.0\.0\.1|0\.0\.0\.0:[0-9]+|http://localhost" --glob '!node_modules' --glob '!*.test.*'
  rg -n "process\.env\.|os\.environ|os\.Getenv|std::env::var|import\.meta\.env" --glob '!node_modules' | head -40
  find . -name '.env.example' -o -name '.env.sample' -o -name 'config.*' -o -name 'settings.*' | grep -v node_modules | head -20
  rg -n "NODE_ENV|APP_ENV|ENVIRONMENT|debug *= *[Tt]rue|DEBUG *= *1" --glob '!node_modules'

Checks:
1. **Hardcoded environment values** -- localhost URLs, ports, absolute `/Users/...` or
   `/home/...` paths, dev API endpoints baked into source instead of config.
2. **Env separation** -- is there any dev/staging/prod distinction, or one hardcoded mode?
3. **`.env.example` completeness** -- does it list the vars the code actually reads? Missing
   vars mean a fresh clone can't run. Extra/never-read vars are cruft.
4. **Secrets via config** -- are credentials read from env (good) or inlined (bad -- overlaps u04)?
5. **Debug left on** -- debug flags, verbose logging, source maps, stack traces exposed, dev
   error pages in a "production" build.
6. **Sensitive data in logs** -- tokens, passwords, PII, full request bodies logged at info.
7. **No build/start story** -- is there a documented, working way to build and run for real?
8. **CORS `*` / auth disabled / open binds** flagged as TODO-for-prod but shipped as-is.

Hard BLOCKER:
- App only works against localhost / hardcoded dev resources with no config path to deploy.
- Secrets or full PII written to logs.

Write findings to `.antislop/findings/u06_config_env_prod.md`.
