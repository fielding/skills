First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: Key Management & Cryptographic Storage

Goal: Audit every cryptographic operation touching seed phrases, private keys, encrypted
blobs, PINs, and biometrics.

Search:
  rg -n "Math\.random|getRandomValues|crypto\.|randomBytes" --type ts
  rg -n "AES|GCM|CBC|CTR|chacha|xchacha|PBKDF2|scrypt|argon|bcrypt|hkdf" --type ts
  rg -n "salt|iv|nonce|iterations|rounds" --type ts
  rg -n "password|pin|biometric|faceid|touchid|keychain|SecureStore|Keystore" --type ts
  rg -n "@scure/bip32|@scure/bip39|@noble|ethers|bitcoinjs|tweetnacl" --type ts

Verify:
1. Key generation uses a CSPRNG (crypto.getRandomValues / randomBytes / trusted lib) — NOT Math.random.
2. Encryption is authenticated (AES-GCM, XChaCha20-Poly1305) — NOT AES-CBC alone.
3. KDF is Argon2id / scrypt / PBKDF2 ≥100k iterations — NOT password used directly as key.
4. Salt random per-wallet (not static); IV/nonce random per-encryption (not reused).
5. PIN is run through a KDF, not used directly as an AES key.
6. No hand-rolled/custom cryptography.
7. Failed-decrypt paths don't leak partial plaintext.
8. Seed not held in app state / clipboard longer than needed; clipboard cleared after display.
9. Mobile uses Keychain/Keystore/SecureStore; extension uses chrome.storage.local — never
   plaintext AsyncStorage / sync storage for key material.

Hard BLOCKERS:
- Math.random for any key material. Custom encryption. AES-CBC without MAC. Static IV/nonce.
  No salt. PIN == AES key (no KDF). Seed/key reaches a logger/analytics/console. Key stored
  unencrypted anywhere.

Write findings to `.antislop/findings/d02_key_management.md`.
