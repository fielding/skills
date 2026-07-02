First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: Secret & Credential Hygiene

Goal: Find committed secrets in current files and git history. NEVER print a full secret --
redact to first-4 + last-4 chars. This is both a slop tell (vibe-coded apps routinely commit
.env) and a hard safety gate.

Scan current files:
  rg -rn "API_KEY|SECRET|PRIVATE_KEY|TOKEN|PASSWORD|PASSWD|MNEMONIC|SEED_PHRASE|SERVICE_ACCOUNT|CLIENT_SECRET|ACCESS_KEY|BEARER|DATABASE_URL.*:.*@" . --glob '!node_modules' --glob '!.git' --glob '!.antislop' -i | head -60
  rg -rn "AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}|xox[baprs]-|-----BEGIN [A-Z]+ PRIVATE KEY-----|eyJ[A-Za-z0-9_-]{20,}\." . --glob '!node_modules' --glob '!.antislop' | head -40
  find . \( -name '*.env*' -o -name '*.pem' -o -name '*.key' -o -name '*.p12' -o -name 'service-account*.json' -o -name '*-adminsdk*.json' \) -not -path '*/node_modules/*'

Git history (secrets often committed then "removed"):
  git log --all --oneline -- '*.env*' '*.pem' '*.key' 2>/dev/null | head -10
  git log --all -S "PRIVATE_KEY" --oneline 2>/dev/null | head -10
  git log --all --diff-filter=D --oneline -- '.env*' 2>/dev/null | head -10

Check:
1. Any real-looking secret in tracked files (not just `.env.example` with placeholders)?
2. Is `.env` (or equivalent) gitignored? Is it accidentally tracked anyway?
3. Secrets shipped to the client bundle (public/ , NEXT_PUBLIC_*, frontend code)?
4. Secrets in git history even if removed from HEAD (still extractable)?
5. Test fixtures with real keys vs. clearly-fake testnet/placeholder values (latter is fine).

Hard BLOCKER:
- Any live-looking secret committed to tracked files or present in git history.
- A private key, mnemonic, or service-account JSON in the repo.
- A real secret in client-shipped code.

Write findings to `.antislop/findings/u04_secret_hygiene.md` (all values redacted).
