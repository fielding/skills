---
name: scrub-ai-tells
description: >-
  Remove LLM writing artifacts from text written on the user's behalf. Scrubs
  em dashes, filler phrases, overly formal language, and patterns that signal
  AI authorship. Use when the user says "scrub", "remove AI tells",
  "make this sound human", "clean up the writing", "make it sound like me",
  or after generating any user-facing text (READMEs, docs, PR descriptions,
  emails, messages). Trigger on /scrub.
allowed-tools: Read, Edit, Glob, Grep
user-invocable: true
---

# Scrub AI-Writing Tells

Remove patterns from text that signal it was written by an LLM. The goal is text that reads like a human wrote it -- direct, natural, and without the polish that gives AI away.

## When to run

- After generating or editing any text the user will publish under their name
- When the user explicitly asks to clean up writing
- As a final pass on READMEs, docs, PR descriptions, commit messages, emails, Slack messages, or any prose

## What to scrub

### Always remove

| Pattern | Replace with |
|---------|-------------|
| Em dashes (--) | Comma, period, parentheses, or restructure the sentence |
| "It's worth noting that..." | Delete or just state the thing |
| "In conclusion" / "To summarize" | Delete |
| "This ensures that..." | Delete or rephrase directly |
| "Additionally" / "Furthermore" / "Moreover" | Delete or use "also" / "and" |
| "In order to" | "To" |
| "Utilize" / "Leverage" | "Use" |
| "Facilitate" | "Help" or "enable" |
| "Comprehensive" | Delete or be specific |
| "Robust" (when vague) | Delete or be specific |
| "Streamline" | "Simplify" or be specific |
| "Seamless" / "Seamlessly" | Delete |
| "Dive into" / "Deep dive" / "Delve" | "Look at" or just start |
| "Let's explore..." | Just start |
| "Overall" (as sentence opener) | Delete |
| "It should be noted" / "Note that" | Just state it |
| "Respectively" (when avoidable) | Restructure |

### Fix structural tells

- **Overly parallel lists**: If 3+ bullet points all start with the same grammatical structure ("Enables X", "Enables Y", "Enables Z"), vary the phrasing.
- **Excessive hedging**: "might", "could potentially", "it may be possible" -- if you know, just say it.
- **Filler transitions**: Sentences that exist only to connect paragraphs but add no content. Delete them.
- **Unnecessary disclaimers**: "While this is a simplified example..." -- just show the example.
- **Over-explanation**: If something is obvious from context, do not explain it.

### Preserve

- Technical accuracy -- never change meaning while scrubbing
- The user's actual voice if they wrote parts of it
- Code blocks, command examples, and technical terms
- Intentional formatting and structure

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
2. Identify every instance of the patterns above.
3. Apply replacements using the Edit tool. Fix all instances in a single pass when possible.
4. Re-read and check that the result reads naturally. A second pass may catch patterns created by the first round of fixes.

### Step 3: Report

Tell the user what was changed. Keep it brief:
- Number of files touched
- Types of changes (e.g., "removed 4 em dashes, replaced 2 filler phrases")
- Flag anything you were unsure about

## Rules

- Never change code, commands, or technical content.
- Never alter meaning. If removing a word changes the meaning, rephrase instead.
- Do not add new content. This skill only removes and rephrases.
- When in doubt about whether something is an AI tell vs. the user's natural style, leave it.
- Em dashes are always removed -- the user has explicitly requested this.

## Examples

**Before:**
```
This tool -- which leverages advanced parsing -- facilitates seamless
integration with your existing workflow. Additionally, it's worth noting
that comprehensive error handling ensures robust operation.
```

**After:**
```
This tool plugs into your existing workflow using standard parsing.
Error handling covers the common failure modes.
```
