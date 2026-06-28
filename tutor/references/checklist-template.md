# Understanding Checklist — template

Copy this into `Understanding-Checklist.md` at the start of a session and keep it current. Every leaf item
carries exactly one status: `Not introduced` · `Introduced` · `Partially understood` · `Verified` ·
`Needs reinforcement`. Start everything at `Not introduced`. Promote an item to `Verified` **only** when
the learner has demonstrated it (explained in own words, applied it, predicted correctly, debugged, or
used a visual model) — never just because you explained it.

Adapt the wording to the actual topic; delete sub-items that genuinely don't apply, but don't quietly drop
a whole area to make the checklist look greener.

```markdown
# Understanding Checklist — <topic>

_Session goal:_ <one line>
_Learner's background:_ <languages / frameworks / systems they already know>
_Requested depth:_ <ELI5 | ELI14 | ELII | default>

## 1. The Problem
- [ ] What problem is being solved? — `Not introduced`
- [ ] Why did this problem exist? — `Not introduced`
- [ ] What inputs / branches / assumptions contributed to it? — `Not introduced`
- [ ] What symptoms revealed it? — `Not introduced`
- [ ] What happens if nothing changes? — `Not introduced`
- [ ] Why understand the problem before the solution? — `Not introduced`

## 2. The Current Behavior
- [ ] What does the system do now? — `Not introduced`
- [ ] Important branches / execution paths? — `Not introduced`
- [ ] What data flows through it? — `Not introduced`
- [ ] What state changes occur? — `Not introduced`
- [ ] What edge cases exist? — `Not introduced`
- [ ] What failure modes exist? — `Not introduced`
- [ ] What's easy to misunderstand here? — `Not introduced`

## 3. The Solution
- [ ] What changed? — `Not introduced`
- [ ] Why this solution over alternatives? — `Not introduced`
- [ ] What design decisions and tradeoffs were made? — `Not introduced`
- [ ] Which edge cases does it handle? — `Not introduced`
- [ ] Which edge cases still need care? — `Not introduced`
- [ ] How does behavior change as a result? — `Not introduced`

## 4. The Broader Context
- [ ] Why does this matter? — `Not introduced`
- [ ] What systems / users / workflows are affected? — `Not introduced`
- [ ] What does it enable later? — `Not introduced`
- [ ] What does it constrain later? — `Not introduced`
- [ ] What risks / maintenance / operational concerns? — `Not introduced`
- [ ] How does it fit the larger architecture or product goal? — `Not introduced`

## 5. Mental Models & Visual Understanding
- [ ] What diagram / table / model best explains this? — `Not introduced`
- [ ] Learner can use the model to explain the concept — `Not introduced`
- [ ] Learner can walk a concrete example through it — `Not introduced`
- [ ] Learner can locate an edge case in it — `Not introduced`
- [ ] Learner can say where the model is simplified / incomplete — `Not introduced`

## 6. Connections to Existing Knowledge
- [ ] Closest familiar construct identified — `Not introduced`
- [ ] How the new concept is similar — `Not introduced`
- [ ] How the new concept differs — `Not introduced`
- [ ] Where the analogy breaks down — `Not introduced`
- [ ] Common traps from over-translating the old model — `Not introduced`
- [ ] The idiomatic way to think about it here — `Not introduced`

## Open questions / needs reinforcement
- <track shaky spots here so they don't get lost>
```
