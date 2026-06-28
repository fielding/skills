---
name: tix
description: >
  Command reference and workflow for the `tix` issue tracker. Stores live in
  per-repo `.tix/` directories. Use whenever you need the exact tix CLI syntax,
  or when creating, listing, updating, searching, or modeling dependencies
  between issues. Pair it with a "use tix in every repo" directive in your agent
  instructions; this skill is the full reference behind it.
allowed-tools: Bash, Read
---

# tix — issue tracker

`tix` tracks issues per-repo in a `.tix/` directory. `.tix/issues.jsonl` is the
source of truth: plain JSONL, git-friendly, one issue per line. Run `tix ready`
before starting work to see what's unblocked.

The tool itself is a standalone binary — install it from
[github.com/fielding/tix](https://github.com/fielding/tix). This skill is just the
command reference and workflow conventions for it.

## Command reference

```
tix init [--prefix name]                     # create .tix/ in current dir
tix add "title" [-p 1-5] [-a who] [-t tag]   # create issue (1 = highest pri)
tix list [--status open] [--assignee x]      # list issues
tix ready [--assignee x]                      # unblocked issues only
tix show <id>                                 # full details + comments
tix status <id> open|in_progress|closed       # change status
tix edit <id> [--title/--body/--priority/--assignee/--add-tag/--rm-tag]
tix comment <id> -m "text" [--author x]       # add comment
tix dep add <id> blocks <target>              # id blocks target
tix search "query"                            # full-text search
```

All list commands support `--json`. Use `-q` to get just the ID back (handy for
scripting: `id=$(tix add "fix login" -p 2 -q)`).

## Workflow

- Check `tix ready` before starting work to find unblocked issues.
- Set an issue `in_progress` when you pick it up, `closed` when it's done.
- Model blocking relationships with `tix dep add <id> blocks <target>` so
  `tix ready` reflects real ordering.
- Log decisions and progress as comments rather than rewriting the body.
- Categorize with tags (`bug`, `enhancement`, etc.).
- Commit `.tix/issues.jsonl` so the tracker travels with the repo. (Note: if `.tix/`
  is in your global gitignore, committing the JSONL in a repo that wants it tracked
  needs `git add -f .tix/issues.jsonl`. Shared/work repos that shouldn't carry a
  personal tracker stay ignored.)

## Notes

- Priorities run 1–5, where 1 is highest.
- `dep add <id> blocks <target>` reads in that direction: `<id>` must finish
  before `<target>` becomes ready.
