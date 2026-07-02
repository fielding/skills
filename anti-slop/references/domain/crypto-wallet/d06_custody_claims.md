First read prompts/shared_rules.md and prompts/findings_schema.md.
Also read .antislop/findings/d01_custody_proof.md if it exists.

# Topic: Custody & Security Claims vs. Proven Reality

Goal: Audit user- and marketing-facing claims specific to a wallet -- "non-custodial",
"audited", "secure", "your keys", endorsements -- against what the audit actually proved. This
is the wallet-specific sharpening of the universal docs-vs-reality topic.

  cat README.md 2>/dev/null
  rg -rn "non.custodial|self.custody|your keys|not your keys|audited|bank.grade|secure|safe|insured|backed by|advised by|reviewed by|partnered with|powered by" . --glob '!node_modules' --glob '!.antislop' -i

For each claim, assess: provably true from code? aspirational/misleading? relies on a
third-party endorsement that may not exist? legal/reputational risk?

Hard BLOCKERS:
- Claims "non-custodial" while d01_custody_proof.md shows NOT CONFIRMED or FALSE.
- Claims "audited by <name>" / "backed by <name>" without documented evidence of that party.
- Uses a real person's or company's name as a trust signal without an agreement.
- Claims "insured", "guaranteed", or "can't lose funds" without basis.
- "Instant" / "zero fee" stated as always-true when it isn't.

Cross-reference every security claim to a specific audit finding. A claim with no supporting
evidence is a confident-lie -- the worst slop signal, amplified by the fact that real money is
involved.

Write findings to `.antislop/findings/d06_custody_claims.md`.
