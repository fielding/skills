# Domain Pack Registry

After the universal + language waves produce a verdict, the orchestrator reads
`.antislop/evidence/stack.md`'s `domain_guess` and consults this table to recommend (or, with
`--deep`/`--domain`, run) the matching domain pack. Domain packs assume anti-slop already ran;
they add only the risk surface unique to that domain and reuse the same engine + verdict format.

| domain_guess | Domain pack | Status |
|---|---|---|
| crypto-wallet | `domain/crypto-wallet` | **bundled** |
| web-api / saas | `domain/web-api` | not built yet |
| ml-app / agent | `domain/ml-app` | not built yet |
| cli-tool / library | (universal usually suffices) | n/a |
| unknown | — | recommend nothing; ask the user |

Behavior:
- **Default**: do NOT run the domain pack. End the verdict with a one-line recommendation and
  the exact command, e.g. `Run the crypto-wallet domain pack: /anti-slop --deep --domain crypto-wallet`.
- **`--deep` or `--domain <name>`**: copy `domain/<name>/*.md` into `.antislop/prompts/`, run
  them as an extra parallel wave (Opus recommended — these are security-critical), then fold
  their findings into the verdict and recompute the score with the domain topics weighted
  heavily (a custody/key BLOCKER caps the score like any other).
- **Not-built domain matched**: recommend a manual deeper review; don't fabricate findings.

### crypto-wallet pack topics
- `d01_custody_proof` — can anyone move funds / recover keys without the user signing?
- `d02_key_management` — RNG, KDF, authenticated encryption, key storage.
- `d03_transaction_safety` — preview == signed; recipient/amount/fee integrity.
- `d04_contract_interactions` — on-chain program / smart-contract authority & escape hatches.
- `d05_platform_integration` — Telegram Mini App / bot identity & platform-policy risk.
- `d06_custody_claims` — "non-custodial"/"audited"/"secure" marketing vs. proven reality.

Adding a domain pack later = drop a `domain/<name>/` folder of topic prompts (same findings
schema), add a registry row, and map a `domain_guess` label to it in `u01_inventory_stack`.
