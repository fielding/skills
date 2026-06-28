First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: Smart Contract & Program Interactions

Goal: Audit on-chain program / smart-contract interactions and their authority model. Skip
sections that don't apply. First check stack.md for what programs/contracts exist.

Solana Anchor (if programs/ or Anchor.toml present):
  cat Anchor.toml 2>/dev/null; find programs/ -name '*.rs' 2>/dev/null
  find programs/ -name lib.rs -exec cat {} \; 2>/dev/null | head -200
Check for: missing signer constraints; missing owner checks; PDA bump not stored/validated;
authority mismatch on privileged instructions; missing has_one; integer overflow (use
checked_*); risky CPI; admin/backend able to unlock a vault without the user's signature;
mutable-by-non-user schedule; emergency admin escape hatch.

EVM (if contracts/ or hardhat/foundry config present):
  find contracts/ -name '*.sol' 2>/dev/null | head -10
Check for: missing access control (onlyOwner/roles) on fund-moving fns; reentrancy;
unchecked external calls; upgradeable proxy with unguarded admin; delegatecall; unbounded
approvals.

Client-side interaction:
  rg -n "programId|Program|Anchor|IDL|ABI|contractAddress" --type ts
  rg -n "approve|delegate|setAuthority|closeAccount|transferFrom" --type ts

For each external program/contract used, document: address/ID · purpose · can it move funds? ·
can it change a vault/lock schedule? · shown to user before signing? · hardcoded or
remote-config-changeable?

Hard BLOCKERS:
- Vault/funds can be unlocked or moved by backend/admin without the user's on-chain signature.
- Unknown program/contract invoked from remotely-provided tx without validation.
- Missing signer/access-control check on a fund-moving or schedule-changing instruction.
- Privileged authority held by a non-user (admin/backend) over user funds.

Write findings to `.antislop/findings/d04_contract_interactions.md`.
