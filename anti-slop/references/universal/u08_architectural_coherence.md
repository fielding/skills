First read prompts/shared_rules.md and prompts/findings_schema.md. Read .antislop/evidence/stack.md.

# Topic: Architectural Coherence & Copy-Paste Drift

Goal: Decide whether one mind (or a coherent process) designed this, or whether it accreted
across disconnected generations. Slop's signature here is N competing patterns for one job and
near-duplicate code that has silently diverged.

Survey structure and patterns:
  find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*' | sed 's/.*\.//' | sort | uniq -c | sort -rn | head
  rg -n "fetch\(|axios|got\(|requests\.|http\.Client|reqwest" --glob '!node_modules' | head -30   # how many HTTP styles?
  rg -n "useState|useReducer|zustand|redux|jotai|recoil|mobx" --glob '!node_modules' | head -20   # how many state libs?
  rg -n "try *\{|\.catch\(|except |Result<|err !=" --glob '!node_modules' | head -20             # error styles

Checks:
1. **Competing patterns for one job** — multiple HTTP clients, multiple state-management
   approaches, two date libs, two ways to read config, two error-handling styles, mixed
   async/callback/promise. Each extra way of doing the same thing is drift.
2. **Near-duplicate code** — the same logic copy-pasted across files with small divergences
   (a bug fixed in one copy, not the others). Spot-check a few suspected clones.
3. **Inconsistent naming/casing/structure** — camelCase next to snake_case for the same
   concept; folders organized by-type in one place and by-feature in another.
4. **Layering violations** — UI reaching into the DB directly in one place, going through a
   service in another; no consistent boundary.
5. **Abstraction churn** — a "helper/util/lib" layer that wraps nothing, or three overlapping
   utils modules.
6. **Conceptual integrity** — does a reader form one mental model, or does each module feel
   like it came from a different project?

Headline: # of competing patterns for core jobs; coherent / mixed / incoherent.

Rarely a standalone BLOCKER, but pervasive drift caps how "real" the project can be — a
codebase no one can hold in their head is a maintenance mirage. Flag the worst as HIGH.

Write findings to `.antislop/findings/u08_architectural_coherence.md`.
