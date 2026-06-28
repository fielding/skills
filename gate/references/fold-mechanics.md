# Fold mechanics: atomic commits, stacked PRs, and rebases

These are the hard-won, general lessons about factoring a loose branch into atomic
commits (stage 9) and folding review fixes back into a *stacked* PR. They are not
specific to any language or project. The expensive-once principle drives all of
them: you split once, after the crew rounds are clean, then keep every later edit
inside the commit it belongs to.

## Expensive steps happen once

Do not open the PR or factor atomic commits until every automated and crew round
is clean. Before that, the branch is loose: one wip commit, amended freely. The
atomic split is a single operation at stage 9, not something repeated after each
finding. This is the whole reason intent + floor + SSM + conventions + mutation +
hygiene + crew + fold all run *before* the split.

## Loose commit, then atomic split once

Stage 6 commits loosely (`git commit -m "wip: ..."`) and pushes so the crew can
branch its worktrees off the remote ref. The diff stays one commit through the
crew+fold loop. Only at stage 9, with the crew clean, do you factor it -- via
`atomic-changes` (the commit form) and `git-factor` (the mechanical split).

Beware `git add -A` during the fold: it sweeps untracked tool-artifact trees
(mutation output, reviewer worktree scratch, `.box`/`.vent`-style dirs) into the
commit. Stage explicit paths, and keep those dirs in `.gitignore`.

## A file can span the stack; split its changes per commit

One file often carries hunks belonging to several commits (a CLI file with a
foundation path, an in-memory demo, and a live path; a module file with `pub mod`
lines added across commits). `git add <file>` for a fixup grabs *all* of that
file's working changes, so it lands in one commit and breaks the others. Split it:
revert the file, re-apply only commit A's hunks (via edits), `commit --fixup=A`,
then stage the rest for B. The revert-and-re-edit route beats hand-built patches
(no whitespace/offset fragility).

## Never resolve an autosquash conflict by copying the "final" file in

Copying the final file drags later-commit content into an earlier commit. The
classic failure: resolving a conflict to "final" pulls a live path that `use`s a
not-yet-declared module into an earlier commit. The branch *tip* stays correct
(net diff identical), so it builds green and the break is invisible -- until the
earlier commit is checked alone, and *that* commit is the base PR's CI head, so it
ships red. Resolve to the correct per-commit content, not the final content.

## Verify each commit standalone, not just the tip

After any fold or rebuild, check out each commit (`git checkout HEAD~n`) and run
the floor (lint + test) on it. Each PR's CI builds that branch's tip = one of
these commits, so a non-bisectable middle commit is a red PR even when the stack
tip is green. Then check the branch back out.

## Confirm the rebuilt tip is net-identical to the known-good one

After conflict resolutions, `git diff <good-sha> HEAD --stat` must be empty -- so
the resolutions did not silently drop or alter content.

## rebase -i edit-marks can silently no-op

`GIT_SEQUENCE_EDITOR` edit-marks sometimes do not take and the rebase completes as
plain picks. When you must edit a specific commit non-interactively, prefer direct
surgery: branch at the commit, `--amend` it, then `cherry-pick` the rest of the
stack on top and re-point the branch refs.

## Pre-existing drift causes conflicts

A file touched in two commits (a doc-comment tweak added later than the commit
that introduced the file) makes a later fold conflict. Resolve to the correct
per-commit content, and consider healing the drift so the file lives in one
commit.

## Slice the safe layers into their own PR

A payoff of transformation-priority ordering (Remove, Fix, Move, Rename, Refactor,
Change, Add, Upgrade, Downgrade): blocking feedback almost never lands in the
leading Remove/Fix/Refactor prep -- it lands in Change/Add. So when a branch carries
both, open the leading Remove/Fix/Refactor commits as their **own PR**, get it
approved and merged (it rarely blocks), then rebase the Change/Add commits onto the
trunk and keep iterating there. Review churn and force-pushes then concentrate on
the small risky slice instead of the whole branch.

For an all-`Add` greenfield feature there is no prep to peel, so the equivalent
slice is at the PR level: a runnable foundation PR (ports + in-memory impl) under a
riskier integration PR (the live client). Even then, expect feedback in the
foundation too, since for greenfield work the foundation is also new `Add` surface.

## Stack rebase mechanics

When a parent's merge or amend moves the tip, rebase the child with cherry-pick (it
handles the parent-overlap cleanly):

```bash
git checkout <child-branch>
git fetch origin
old_child_tip=$(git rev-parse HEAD)
git reset --hard origin/<new-parent-or-trunk>
git cherry-pick $old_child_tip
# resolve conflicts: take the new parent's structure, layer the child's additions on top
```

Then re-run the pipeline from the floor.

**When a sibling merges into the trunk after your stack was cut.** If a cousin PR
(a concrete impl your new layer depends on) merges into the trunk *after* your
stacked branches were cut from an older trunk, neither the trunk nor your branch
has everything: the trunk has the sibling but not your stack, your branch has your
stack but not the sibling. Rebase the whole stack onto the current trunk bottom-up
(cherry-pick each branch onto the rebased parent) so the chain is linear and every
layer sees the sibling's merged code. Force-push each; the in-review PRs just
update. Do this before building a new layer that needs all of it.
