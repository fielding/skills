First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: Non-Custodial Proof (the fundamental claim)

MOST IMPORTANT wallet topic. Answer from code evidence, not claims.

Primary question: Can any server, admin, cloud function, bot, remote config, API route, or
third-party service move user funds or recover private keys — WITHOUT the user's explicit
signing action on the client?

Search comprehensively:
  rg -n "mnemonic|seed|seedPhrase|privateKey|secretKey|keypair" --type ts
  rg -n "createWallet|importWallet|generateWallet|recoverWallet" --type ts
  rg -n "encrypt|decrypt|backup|cloud" --type ts
  rg -rn "localStorage|indexedDB|sessionStorage|chrome\.storage" --type ts
  rg -n "firestore|firebase|supabase|mongodb|prisma" --type ts -l
  rg -n "signTransaction|signAndSend|sendTransaction" --type ts

For every function touching seed/key material, trace:
1. Where is it called from? 2. Does it cross a network boundary? 3. Does it land in a log?
4. Does it reach a database write? 5. If an encrypted blob leaves the device, where does it go,
and is the decryption key ever also sent?

Check:
- Backend/cloud functions — can any be called with a userId to return signing material or move funds?
- API routes — do any accept or return decrypted wallet material?
- mobile/ — OS-protected keychain (Keychain/Keystore/SecureStore) or plain storage?
- extension/ — `chrome.storage.local` (not `sync`) for key material?
- Any "recovery" or "support" path that reconstructs keys server-side?

Final statement (required):
- Non-custodial claim: CONFIRMED / NOT CONFIRMED / FALSE — with evidence.

Hard BLOCKERS:
- Seed/private key sent to backend, written to any DB, or present in any log.
- Admin/support recovery path exists. Server-side signing exists. Backend generates wallets.
- Remote config can redirect funds without user re-signing.

Write findings to `.antislop/findings/d01_custody_proof.md`.
