First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: Transaction Safety

Goal: Audit every path that creates, previews, signs, or sends transactions. Answer: can a
server, API response, or malicious input cause funds to move without clear user consent, or
differently from what the user saw?

Trace, per chain present (Solana/EVM/Bitcoin/TON/...):
  rg -n "signTransaction|signAndSend|sendTransaction|buildTransaction|createTransaction" --type ts
  rg -n "recipient|destination|\bto\b|amount|value|lamports|wei|satoshi|fee" --type ts
  rg -n "Jupiter|swap|slippage|priorityFee|0x" --type ts
  rg -n "username|payname|resolve|ens|\.sol\b" --type ts

For each flow, document: | User Action | File | Tx built by | Backend involved? | Remote config? | User preview? | Signer | Main risk |

Check:
1. Preview shows the EXACT transaction that will be signed.
2. Recipient address shown and confirmed. 3. Amount shown and confirmed. 4. Fees disclosed.
5. Can a backend response change the recipient/amount AFTER preview but before sign?
6. Can name resolution (username/ENS) resolve to a different address at sign time than preview?
7. Swap/aggregator transactions decoded and validated before signing; slippage capped.
8. Externally-built transactions checked against a program/contract allowlist.
9. Approvals/delegations (approve, setAuthority, closeAccount) shown with explanation.
10. Simulation before send; stale-blockhash/deadline handling.

Hard BLOCKERS:
- User signs a backend-provided transaction with no client-side validation.
- Recipient or amount not shown before signing.
- Fee/destination controlled by remote config without per-tx user approval.
- Swap tx accepted from API without decoding. Name resolves differently at sign vs preview.

Write findings to `.antislop/findings/d03_transaction_safety.md`.
