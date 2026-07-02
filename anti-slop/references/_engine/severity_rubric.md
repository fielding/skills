# Severity Rubric -- Anti-Slop

Severity is the score's weak point: independent per-topic agents grade BLOCKER vs HIGH
inconsistently, and that inconsistency is what moves a repo across the Go/No-Go line. Grade
every finding with this ONE bar so severities mean the same thing across topics. Both the
per-topic agents (first pass) and the severity-normalization pass use this file.

## Step 1 -- classify the axis
- **Realness** (substance): the code is fake/hollow/broken -- doesn't build, a core feature is a
  stub, zero real tests on core logic.
- **Safety**: security / funds / data -- injection, RCE, auth bypass, fund movement, secret
  exposure, data loss.
- **Quality**: maintainability / reliability -- drift, dead code, missing tests on non-critical
  paths, no linter, DoS.

## Step 2 -- the reachability test (the #1 disambiguator)
Ask: **who can trigger this, and what do they get?**
- **Untrusted / any user / attacker-controlled input** reaching a dangerous sink → top of scale.
- **Authenticated-but-not-privileged** actor crossing a boundary they shouldn't → still high.
- **Trusted local operator only** (e.g. a CLI dev tool's own `shell=True` on their own machine,
  reachable only by the person running it) → cap at MEDIUM. Local-only ≠ ship-blocking.

This is the tie-breaker that caused most of the drift. A fork-PR RCE (any contributor → code
exec on your runner) is a BLOCKER; a `shell=True` call only the local operator can invoke is a
MEDIUM -- same mechanism, different reachability.

## Step 3 -- grade

**BLOCKER** -- do not ship / do not trust until fixed. Any of:
- Realness-fatal: doesn't build/typecheck; a core advertised feature is a stub/absent; zero real
  tests on core logic. (These ALSO cap the Substance Score -- see verdict_template.md.)
- Untrusted-reachable path to: fund/asset movement without proper auth or user consent; RCE /
  code or command injection; SQL/NoSQL injection; auth or authorization bypass; reading/writing
  other users' data; unsafe deserialization of attacker-controlled data.
- A committed **live** secret (real key/token/credential in the tree or git history).
- A safety/custody/"audited" claim the code contradicts (a confident-lie about security).

**HIGH** -- real, will bite real users or a maintainer soon, but not untrusted-catastrophic:
- Missing tests on important logic that is NOT directly fund/auth-moving.
- Secret/credential **exposure** that needs another foothold (e.g. API key logged to console).
- Copy-paste drift that has already produced a wrong result on one path.
- A safety bug reachable only by an authenticated, non-malicious mistake.
- Builds, but lint/type errors would fail CI / `next build`.
- Green CI that doesn't actually test/typecheck what it claims (confident-lie, non-catastrophic).

**MEDIUM** -- should fix; bounded blast radius:
- Local-operator-only injection (per the reachability test).
- DoS / ReDoS with no integrity or confidentiality loss.
- Quality issues with real but contained impact; undocumented required config.

**LOW / INFO** -- minor, cosmetic, defense-in-depth, stale docs, style, unused deps.

## Worked anchors (from calibration -- grade new findings to match these)
| Finding | Grade | Why |
|---|---|---|
| Web/Telegram API trusts client-supplied `user_id`, no auth (any client moves/reads others' data) | BLOCKER | untrusted-reachable auth bypass |
| Bundled CI runs gate scripts from the PR tree (fork-PR → RCE on runner) | BLOCKER | untrusted contributor → code exec |
| Telegram webhook never verifies its secret token | BLOCKER | untrusted caller drives privileged action |
| Paid action charges a credit then dead-codes the refund (charged for failures) | HIGH | money correctness, not theft/loss of principal |
| Mainnet RPC URL+api-key logged to the browser console | HIGH | secret exposure, needs console/log access to exploit |
| Fund-moving instruction builders have zero tests | HIGH | high-risk untested code, not itself an exploit |
| `shell=True` scripts reachable only by the local operator | MEDIUM | trusted-local reachability cap |
| O(n²) ReDoS in a parser reachable from untrusted input | MEDIUM | availability only -- no integrity/confidentiality |
| CI "type" job silently checks 2 of N packages, hiding 144 type errors | HIGH | confident-lie: green CI ≠ checked |
| Test fixtures contain public testnet keys clearly marked fake | INFO | not a live secret |

When two findings are comparable, grade them the same. If torn between two levels, state the
reachability fact that breaks the tie and pick the lower level only if untrusted reach is
genuinely absent.
