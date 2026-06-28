First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: Platform Integration (Telegram Mini App / Bot)

Goal: If the wallet integrates with Telegram (or a similar embedding platform), audit identity
verification and platform-policy risk. Skip if no such integration exists.

  rg -n "initData|initDataUnsafe|WebApp|Telegram|tgWebApp" --type ts
  rg -n "bot_token|BOT_TOKEN|webhook" --type ts
  rg -n "user\.id|from\.id|telegramId" --type ts
  rg -n "HMAC|hmac|createHmac|sha256" --type ts
  rg -n "TON|tonconnect|TonConnect|start_param" --type ts

Check:
1. Is Telegram `initData` validated SERVER-SIDE via HMAC-SHA256 with the bot token (hash field
   removed before computing)? Or is the client-supplied user identity simply trusted?
2. Replay protection: is `auth_date` checked and stale initData (>5 min) rejected?
3. Bot token stored server-side only — never shipped to the client?
4. Are wallet actions gated on validated initData, or on any Telegram session?
5. Sensitive values passed in `start_param` / Mini App URL?
6. Does the app also run outside Telegram? Is that path secured too?
7. Webhook endpoint protected, or callable by anyone?
8. Platform-policy: does the integration risk a ban (e.g. blockchain features where the
   platform requires TON Connect)?

Hard BLOCKERS:
- Trusts Telegram user identity without validating initData HMAC.
- Bot token exposed client-side. No replay protection on initData.
- A bot command can initiate or pre-fill a transaction without client-side user signing.

Write findings to `.antislop/findings/d05_platform_integration.md`.
