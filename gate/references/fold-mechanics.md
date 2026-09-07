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

Include any CI-armed diff-aware gates the local floor never runs (added-line
lints computed from the PR diff and the like): run them per rewritten commit
against that commit's own base. A mid-stack commit can fail such a gate while
the tip passes it, and the mid-stack commit is what some PR's CI actually
checks.

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

**Propagating a mid-stack amend through a deep stack.** With one branch per
stacked PR on a long linear chain, a single rebase moves every descendant ref at
once instead of N cherry-picks:

```bash
git rebase --onto <amended-commit> <old-commit> <topmost-branch> --update-refs
```

Three traps, each verified the hard way:

- `--update-refs` never moves a branch that points *at* `<old-commit>` itself --
  the upstream bound is exclusive. When the amended commit is also some branch's
  head, repoint that branch by hand (`git branch -f`). Missing it silently breaks
  the chain at that boundary and leaves the un-amended head to ship.
- Re-verify linearity after *every* propagation, not once up front: each branch
  head must be an ancestor of the next, and the total commit count must be
  unchanged.
- Push with exact leases read from the remote at push time (`git ls-remote`),
  not from local `origin/*` refs. After several rewrites the remote-tracking
  refs go stale and `--force-with-lease=<ref>:<stale-sha>` is rejected with
  "stale info".

**When a sibling merges into the trunk after your stack was cut.** If a cousin PR
(a concrete impl your new layer depends on) merges into the trunk *after* your
stacked branches were cut from an older trunk, neither the trunk nor your branch
has everything: the trunk has the sibling but not your stack, your branch has your
stack but not the sibling. Rebase the whole stack onto the current trunk bottom-up
(cherry-pick each branch onto the rebased parent) so the chain is linear and every
layer sees the sibling's merged code. Force-push each; the in-review PRs just
update. Do this before building a new layer that needs all of it.

## When fixups span the stack, split a wip instead of autosquashing

A `fixup!` authored against the *full* stack carries context from later commits, so
`rebase --autosquash` conflicts the moment it replays that fixup onto its target,
and every conflict tempts the copy-the-final-file mistake above. When more than a
couple of fixups touch files that several commits share, do not autosquash. Rebuild
the whole change as one wip commit on the current base (`cherry-pick -n` the range,
verify the tree is byte-identical to the known-good tip), then factor that single
commit with `git factor`, driving each atom from a deterministic state generator
that slices the *final* files into cumulative per-atom states (self-test: the last
state must reproduce the final tree exactly). The split then happens once and every
intermediate tree is derived, never hand-typed.

## Factor-gate hygiene

Traps that each cost a factor session:

- A docs-only atom matches zero tests; `cargo nextest` errors on "no tests to run"
  unless the gate passes `--no-tests=pass`.
- Guards built on `git status --porcelain` see a new directory collapsed to
  `dir/`, not the file inside it; use `--porcelain -uall`.
- `git factor --exec` and driver scripts run in non-interactive shells that lack
  version-manager shims (fnm's `yarn`, `node`); export the shim bin dir into PATH
  explicitly, and check exit codes directly rather than through pipes.
- `git cherry-pick` has no `-q`; and a conflicted `cherry-pick -n` leaves no
  sequencer, so `--abort` has nothing to abort: recover with `git reset --hard`
  to the last good commit.
- Verify each commit in a *fresh* worktree, but give it the gitignored build
  products the gates need (node_modules, a generated ORM client) or the failure
  is the environment, not the commit.

## Splitting a `#[cfg(test)]` module trips `dead_code`

Fields that only a later atom reads (a corpus DTO whose request fields the replay
driver consumes) warn as never read in the earlier atom, and `deny(warnings)` turns
that into a red gate. Derived `Clone`/`Debug` do not count as reads; a proc-macro
derive such as `Serialize` does, which is why removing a speculative derive can
expose the gap. The fix is the honest one: the earlier atom's tests read every
field it parses. If a field truly has no reader until the later atom, the field
belongs to that atom. The same rule orders a new module's atoms: land the type and
its first consumer together (an event plus the handler that emits it), then the
helpers whose only caller is the next atom (a parser plus the observer that feeds it).
