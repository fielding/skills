---
name: scrub-ai-tells
description: >-
  Remove LLM writing artifacts from text written on the user's behalf. Scrubs
  em dashes, filler phrases, overly formal language, and structural patterns
  that signal AI authorship. Use when the user says "scrub", "remove AI tells",
  "clean up the writing", or after generating any user-facing text (READMEs,
  docs, PR descriptions, commit messages, emails, messages). Trigger on /scrub.
allowed-tools: Read, Edit, Glob, Grep
user-invocable: true
---

# Scrub AI-Writing Tells

Remove patterns from text that signal it was written by an LLM. The goal is text that reads like a human wrote it -- direct, natural, and without the polish that gives AI away.

## Lane boundary (read first)

This skill is the **mechanical** pass for **un-voiced** text: READMEs, docs, PR descriptions, commit messages, and generic prose where the only goal is "don't sound like an AI wrote it."

For text that should sound like a *specific person* (Fielding's voice), the `my-voice` skill owns the pass, including its own AI-tell scan. **Do not run scrub over `my-voice` output.** `my-voice` deliberately keeps some of the words and constructions this skill removes (e.g. "leverage", "facilitate", a single lopsided "not X but Y", one earned closer); scrubbing that text would destroy choices `my-voice` made on purpose. The router is which skill was invoked, not a judgment about the text -- if the user wants their voice, that is `my-voice`'s job, not this one.

## When to run

- After generating or editing un-voiced text the user will publish
- When the user explicitly asks to clean up writing
- As a final pass on READMEs, docs, PR descriptions, commit messages, emails, or any generic prose

## What to scrub

### Always remove (lexical)

| Pattern | Replace with |
|---------|-------------|
| Em dashes (--) | Comma, period, parentheses, or restructure the sentence |
| "It's worth noting that..." | Delete or just state the thing |
| "In conclusion" / "To summarize" / "Ultimately" | Delete |
| "This ensures that..." | Delete or rephrase directly |
| "Additionally" / "Furthermore" / "Moreover" | Delete or use "also" / "and" |
| "In order to" | "To" |
| "Utilize" / "Leverage" | "Use" |
| "Facilitate" | "Help" or "enable" |
| "Foster" / "Empower" | Be specific about the actual effect |
| "Paradigm shift" / "Game changer" | Delete or say what actually changed |
| "Comprehensive" | Delete or be specific |
| "Robust" (when vague) | Delete or be specific |
| "Streamline" | "Simplify" or be specific |
| "Seamless" / "Seamlessly" | Delete |
| "Dive into" / "Deep dive" / "Delve" | "Look at" or just start |
| "Overall" (as sentence opener) | Delete |
| "It should be noted" / "Note that" | Just state it |
| "Respectively" (when avoidable) | Restructure |

Do not blind-ban ambiguous real words (e.g. "harness", "elevate", "surface") -- only remove them when they are clearly the vague-AI usage, not a legitimate one.

(`my-voice` deliberately keeps some of these for voiced text; that skill's list wins for text it owns. See the lane boundary above.)

### Fix structural tells

These are unconditional in scrub's lane -- for un-voiced text they are essentially always tells. The example phrases inside these bullets fire only when the *pattern* is present (the rhetorical setup, the copula substitution), not on the bare word in ordinary use -- "the CLI offers two modes" and "a fundamentally different design" are fine.

- **Overly parallel lists**: If 3+ bullet points all start with the same grammatical structure ("Enables X", "Enables Y", "Enables Z"), vary the phrasing.
- **Throat-clearing / announce openers**: "Here's the thing," "Let me be clear," "I'll be honest," "Look," "Here's what you need to know," "Without further ado," "Let's dive in," "Let's explore," -- delete and state the point.
- **Faux-insight / authority tropes / rhetorical setups**: "What most people get wrong," "Here's what nobody tells you," "What if I told you," "Think about it," "Plot twist," "at its core," "what really matters," "fundamentally," "the real question is" -- drop the setup or ceremony, let the claim stand on its own.
- **Fake-strong verbs (copula avoidance)**: "serves as a centralized hub for," "acts as a bridge between," "boasts," "features," "offers," "stands as" -- use "is" / "are" / "has" plus the specific detail.
- **Importance puffery**: "stands as a testament to," "marks a pivotal moment," "plays a crucial role" -- state the plain fact and let the reader judge.
- **Superficial "-ing" analysis clauses**: trailing "...highlighting the fact that," "...underscoring the need for," "...showcasing" that fake an explanation. Delete the clause. If the sentence collapses without it, apply the flag-don't-invent rule below.
- **Colon reveals**: a noun phrase + colon + a single dramatic payoff ("The result: everything changed"). Rewrite as a plain sentence. This only applies to the dramatic-reveal form -- **leave list-introducing, label, and definition colons alone** ("Requirements: Node 18+", "Note:", "Error: file not found"), which are normal and dominant in docs.
- **Fake-profound kickers**: a final aphorism or metaphor line that adds no information. If the last line carries the actual takeaway, keep the takeaway and cut the flourish; if it is pure flourish, delete it. Do not rewrite it into a *better* metaphor -- the move itself is the tell. This includes generic upbeat conclusions ("the future looks bright," "exciting times ahead") -- cut them or end on the last concrete fact.
- **Negative listing / dramatic fragmentation**: "Not X. Not Y. Z." or "X. And Y. And Z." -- state the point in complete sentences.
- **Excessive hedging**: "might", "could potentially", "it may be possible" -- if you know, just say it.
- **Filler transitions**: sentences that only connect paragraphs but add no content -- delete them.
- **Unnecessary disclaimers**: "While this is a simplified example..." -- just show the example.
- **Over-explanation**: if something is obvious from context, do not explain it.
- **Weasel attribution**: "experts agree," "studies show," "it's widely known" -- if the actual source is present in the surrounding text or context, name it; otherwise flag it to the user. Never invent a source, and never silently keep the weasel phrase.
- **Elegant variation (synonym cycling)**: swapping in synonyms to avoid repeating a word ("the protagonist ... the character ... the figure ... our hero"). Repeat the plain term or restructure; forced variety is a tell, not good style.
- **False ranges**: "from X to Y" where X and Y are not endpoints of a real scale ("everything from onboarding to analytics"). List the items plainly instead.
- **Diff-anchored writing**: describing a thing by what changed rather than what it is ("now supports," "no longer requires," "has been updated to"). In a README or doc, describe the current state directly; keep change-narration to changelogs, migration guides, PR descriptions, and commit messages (where narrating the change is the whole point).
- **Chatbot-leak phrasing**: assistant-to-user artifacts that survived into standalone published text (READMEs, docs) -- "I hope this helps," "Certainly!," "Great question," "Want me to." Delete; the text should stand alone. (In an actual email or message, "let me know if you have questions" is ordinary human phrasing -- leave it.)
- **Uniform hyphenation**: hyphenate a compound modifier only before the noun ("a high-quality report"), not in predicate position ("the report is high quality"). AI hyphenates both; fix the predicate cases -- except compounds that keep the hyphen in every position (self-* forms, dictionary-listed compounds like "well-being").
- **Decorative boldface**: bold on every key phrase or term. Keep bold only where it genuinely aids scanning; strip the rest.

### Preserve

- Technical accuracy -- never change meaning while scrubbing
- Any of the user's own writing mixed into the text
- Code blocks, command examples, and technical terms
- Intentional formatting and structure

## Weight clusters, not isolated tells

Scrub is looking for AI *slop*, which shows up as a cluster of these tells, not a single ordinary word. Do not rewrite text solely for:

- Clean grammar or a consistent style -- careful writers exist.
- A single common transition, or one "honestly" / "look" mid-sentence (the tell is the theatrical *opener*, not the word).
- An ordinary unsourced statement -- only fake-authority attribution ("experts agree") is a weasel tell, not every claim without a citation.
- Mixed or formal register on its own.
- One short emphatic sentence.

This discipline governs the ambiguous lexical items (see "do not blind-ban" above) and single-instance judgment calls. It does **not** relax two things: em dashes are still always removed (the captain's standing rule), and the structural tells above stay in force as written (several carry their own scope conditions, e.g. colon reveals and decorative boldface).

## The flag-don't-invent rule

Scrub only removes and rephrases; it never adds facts. When a clean fix would require information the text does not contain -- the real source behind a weasel attribution, the actual mechanism behind an "-ing" clause, a claim that only makes sense with a missing detail -- do **not** invent it. Flag it to the user and leave the text as-is for that spot.

## Modes

### Edit (default)

Rewrite in place and report what changed.

### Detect-only

When the user says "detect", "just flag it", "report only", or passes `--check`: for each tell, report a short quote (cap ~125 chars), name the pattern, and give the suggested fix. Make **no** edits. Do not score the text or claim it was AI-written.

## Workflow

### Step 1: Identify target files

If the user specifies files, use those. Otherwise, check recently modified files:
```
git diff --name-only HEAD~1
```
Filter to prose files: .md, .txt, .rst, or any file the user is clearly writing for human readers.

### Step 2: Scan and fix

For each file:

1. Read the full file.
2. Identify every instance of the lexical and structural patterns above.
3. Apply replacements using the Edit tool. Fix all instances in a single pass when possible.
4. Re-read and check that the result reads naturally. A second pass may catch patterns created by the first round of fixes.

### Step 3: Report

Tell the user what was changed. Keep it brief:
- Number of files touched
- Types of changes (e.g., "removed 4 em dashes, replaced 2 filler phrases, cut 1 fake-profound kicker")
- Everything caught by the flag-don't-invent rule, so the user can supply the missing fact

## Rules

- Never change code, commands, or technical content.
- Never alter meaning. If removing a word changes the meaning, rephrase instead.
- Do not add new content. This skill only removes and rephrases; missing facts get flagged, not invented.
- When in doubt about whether something is an AI tell vs. the user's natural style, leave it.
- Em dashes are always removed -- the user has explicitly requested this.
- Do not run this skill over `my-voice` output (see the lane boundary).

## Examples

**Before:**
```
This tool -- which leverages advanced parsing -- facilitates seamless
integration with your existing workflow. Additionally, it's worth noting
that comprehensive error handling ensures robust operation. The result:
a tool that just works.
```

**After:**
```
This tool plugs into your existing workflow using standard parsing.
Error handling covers the common failure modes.
```
