#!/usr/bin/env python3
"""
read-recent-session.py  --  vendored, self-contained recent-session reader for the
`intent` skill (gate pipeline, stage 0).

Find the most recent agent session(s) whose working directory matches the current
repo and print a readable transcript so the calling agent can summarize the WHY of
the change just made. Supports Claude Code (primary), Codex CLI, and pi-mono.

This is a focused trim of skill-distill's transcript parsers. It does NOT mine,
merge, cluster, or generate skills -- it just locates and reads the newest
relevant session(s). `intent` must install and run without skill-distill present.

Transcript stores:
  Claude Code : ~/.claude/projects/<encoded-cwd>/<session-uuid>.jsonl
                Each line carries its own `cwd`, `gitBranch`, `timestamp` (ISO),
                and `message.{role,content}`. content is a str or a list of blocks
                ({type: text|thinking|tool_use|tool_result, ...}).
  Codex CLI   : ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl
                Lines are {type, payload}; payload is an OpenAI Responses item.
                A `session_meta` header carries payload.cwd.
  pi-mono     : ~/.pi/agent/sessions/--<encoded-path>--/<ts>_<uuid>.jsonl
                Tree of entries; chat payload nested under `message.{role,content}`.
                cwd comes from the header entry (or decoded from the dir name).

The reliable repo match is each transcript's recorded `cwd` (we match the repo
root prefix), NOT the lossy encoded directory name.

Usage:
    read-recent-session.py [--repo PATH] [--tool claude|codex|pi|all]
                           [--count N] [--max-chars N] [--days N]
                           [--include-tools] [--list]

    --repo PATH       Repo root to match (default: `git rev-parse --show-toplevel`
                      of the cwd, falling back to the cwd itself).
    --tool            Which store(s) to search. Default: all. Newest session
                      across the chosen stores wins regardless of tool.
    --count N         Number of recent sessions to print (default: 1).
    --max-chars N     Truncate each turn's text to N chars (default: 4000).
    --days N          Ignore sessions older than N days (default: 30).
    --include-tools   Include one-line summaries of tool_use / tool_result turns.
                      Off by default (intent cares about the WHY, not tool noise).
    --list            Only list the matching sessions (path, tool, mtime, branch),
                      do not print transcripts.

Output is plain text on stdout, with a light secret redaction pass applied so
pasted API keys / tokens / op:// refs never reach the caller.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# --------------------------------------------------------------------------- #
# Secret redaction (light pass -- defense in depth; intent.md must stay clean) #
# --------------------------------------------------------------------------- #

_SECRET_PATTERNS = [
    # 1Password secret references
    (re.compile(r"op://[^\s'\"]+"), "[redacted op:// ref]"),
    # Bearer / Authorization headers
    (re.compile(r"(?i)\b(authorization|bearer)\s*[:=]?\s*[A-Za-z0-9._\-]{12,}"),
     r"\1 [redacted]"),
    # Common provider key shapes: sk-..., ghp_..., github_pat_..., xoxb-..., AKIA...
    (re.compile(r"\b(sk|rk|pk)-[A-Za-z0-9_\-]{16,}"), "[redacted key]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "[redacted gh token]"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"), "[redacted gh pat]"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}"), "[redacted slack token]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[redacted aws key]"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}"), "[redacted google key]"),
    # JWTs
    (re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{6,}"),
     "[redacted jwt]"),
    # KEY/TOKEN/SECRET/PASSWORD = longish value
    (re.compile(r"(?i)\b([A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API)[A-Z0-9_]*)"
                r"\s*[:=]\s*['\"]?([A-Za-z0-9._\-/+]{12,})['\"]?"),
     r"\1=[redacted]"),
]


def redact(text: str) -> str:
    if not text:
        return text
    for pat, repl in _SECRET_PATTERNS:
        text = pat.sub(repl, text)
    return text


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #

def normalize_ts(ts) -> int:
    """Normalize a timestamp (ISO string, seconds, or ms) to epoch milliseconds."""
    if not ts:
        return 0
    if isinstance(ts, str):
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return int(dt.timestamp() * 1000)
        except Exception:
            return 0
    val = int(ts)
    return val * 1000 if val < 32503680000 else val


def resolve_repo(arg_repo: str | None) -> Path:
    if arg_repo:
        return Path(arg_repo).resolve()
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, cwd=os.getcwd(),
        )
        if top.returncode == 0 and top.stdout.strip():
            return Path(top.stdout.strip()).resolve()
    except Exception:
        pass
    return Path(os.getcwd()).resolve()


def cwd_matches(repo: Path, cwd: str) -> bool:
    """True if `cwd` is inside (or equal to) the repo root."""
    if not cwd:
        return False
    try:
        c = Path(cwd).resolve()
    except Exception:
        return False
    return c == repo or repo in c.parents


def clip(text: str, n: int) -> str:
    text = text.strip()
    if len(text) <= n:
        return text
    return text[:n].rstrip() + f"\n... [truncated, {len(text) - n} more chars]"


# --------------------------------------------------------------------------- #
# Session model                                                               #
# --------------------------------------------------------------------------- #

class Session:
    def __init__(self, path: Path, tool: str):
        self.path = path
        self.tool = tool
        self.cwd = ""
        self.branch = ""
        self.last_ts = 0          # newest turn timestamp (ms)
        self.turns: list[tuple[str, str]] = []  # (label, text)

    def sort_key(self):
        # Prefer recorded last turn ts; fall back to file mtime.
        return self.last_ts or int(self.path.stat().st_mtime * 1000)


# --------------------------------------------------------------------------- #
# Claude Code reader                                                           #
# --------------------------------------------------------------------------- #

def parse_blocks(content, include_tools: bool, max_chars: int) -> list[tuple[str, str]]:
    """Turn a Claude/Anthropic-style content (str or block list) into labeled turns."""
    out = []
    if isinstance(content, str):
        t = content.strip()
        if t:
            out.append(("text", clip(redact(t), max_chars)))
        return out
    if not isinstance(content, list):
        return out
    for b in content:
        if not isinstance(b, dict):
            continue
        bt = b.get("type")
        if bt == "text":
            t = (b.get("text") or "").strip()
            if t:
                out.append(("text", clip(redact(t), max_chars)))
        elif bt == "thinking":
            t = (b.get("thinking") or "").strip()
            if t:
                out.append(("thinking", clip(redact(t), max_chars)))
        elif bt == "tool_use" and include_tools:
            name = b.get("name", "tool")
            inp = b.get("input", {})
            summary = ""
            if isinstance(inp, dict):
                summary = inp.get("command") or inp.get("description") \
                    or inp.get("file_path") or inp.get("pattern") or ""
            out.append(("tool_use", redact(f"{name}: {str(summary)[:200]}")))
        elif bt == "tool_result" and include_tools:
            c = b.get("content")
            if isinstance(c, list):
                c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
            out.append(("tool_result", clip(redact(str(c)), 400)))
    return out


def read_claude_sessions(repo: Path, cutoff_ms: int, include_tools: bool,
                         max_chars: int, include_subagents: bool = False) -> list[Session]:
    base = Path.home() / ".claude" / "projects"
    if not base.exists():
        return []
    sessions = []
    for jf in base.rglob("*.jsonl"):
        # Subagent sidechains live under <session>/subagents/. They reflect the
        # agent talking to itself, not the human-stated WHY, so skip them by
        # default -- intent wants the top-level conversation.
        if not include_subagents and "subagents" in jf.parts:
            continue
        try:
            if jf.stat().st_mtime * 1000 < cutoff_ms:
                continue
        except OSError:
            continue
        s = Session(jf, "claude")
        matched = False
        try:
            with open(jf, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        o = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if o.get("cwd") and not s.cwd:
                        s.cwd = o["cwd"]
                    if o.get("gitBranch"):
                        s.branch = o["gitBranch"]
                    if o.get("cwd") and cwd_matches(repo, o["cwd"]):
                        matched = True
                    if o.get("type") not in ("user", "assistant"):
                        continue
                    msg = o.get("message", {})
                    if not isinstance(msg, dict):
                        continue
                    role = msg.get("role", o.get("type"))
                    ts = normalize_ts(o.get("timestamp"))
                    if ts > s.last_ts:
                        s.last_ts = ts
                    for label, text in parse_blocks(msg.get("content"),
                                                    include_tools, max_chars):
                        s.turns.append((f"{role}/{label}", text))
        except (OSError, IOError):
            continue
        if matched and s.turns:
            sessions.append(s)
    return sessions


# --------------------------------------------------------------------------- #
# Codex CLI reader                                                             #
# --------------------------------------------------------------------------- #

_INJECTED = ("<environment_context>", "<user_instructions>",
             "# AGENTS.md", "# Context from my IDE")


def read_codex_sessions(repo: Path, cutoff_ms: int, include_tools: bool,
                        max_chars: int) -> list[Session]:
    base = Path.home() / ".codex" / "sessions"
    if not base.exists():
        return []
    sessions = []
    for jf in base.rglob("rollout-*.jsonl"):
        try:
            if jf.stat().st_mtime * 1000 < cutoff_ms:
                continue
        except OSError:
            continue
        s = Session(jf, "codex")
        try:
            with open(jf, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        o = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    etype = o.get("type", "")
                    payload = o.get("payload") if isinstance(o.get("payload"), dict) else {}
                    if etype in ("session_meta", "session_start", "metadata",
                                 "header", "init"):
                        s.cwd = payload.get("cwd") or payload.get("workingDir") \
                            or o.get("cwd") or s.cwd
                        continue
                    item = payload or o
                    role = item.get("role", "")
                    itype = item.get("type", "")
                    if not (role in ("user", "assistant", "human")
                            or itype in ("message",)):
                        continue
                    content = item.get("content") or item.get("text") or ""
                    if isinstance(content, list):
                        parts = []
                        for blk in content:
                            if isinstance(blk, dict):
                                parts.append(blk.get("text", ""))
                            elif isinstance(blk, str):
                                parts.append(blk)
                        content = " ".join(p for p in parts if p)
                    content = str(content).strip()
                    if not content or content.lstrip().startswith(_INJECTED):
                        continue
                    ts = normalize_ts(o.get("timestamp") or item.get("timestamp"))
                    if ts > s.last_ts:
                        s.last_ts = ts
                    s.turns.append((f"{role or 'msg'}/text",
                                    clip(redact(content), max_chars)))
        except (OSError, IOError):
            continue
        if s.cwd and cwd_matches(repo, s.cwd) and s.turns:
            sessions.append(s)
    return sessions


# --------------------------------------------------------------------------- #
# pi-mono reader                                                              #
# --------------------------------------------------------------------------- #

def decode_pi_path(encoded: str) -> str:
    return "/" + encoded.strip("-").replace("-", "/")


def read_pi_sessions(repo: Path, cutoff_ms: int, include_tools: bool,
                     max_chars: int) -> list[Session]:
    base = Path.home() / ".pi" / "agent" / "sessions"
    if not base.exists():
        return []
    sessions = []
    for d in base.iterdir():
        if not d.is_dir():
            continue
        decoded = decode_pi_path(d.name)
        for jf in d.glob("*.jsonl"):
            try:
                if jf.stat().st_mtime * 1000 < cutoff_ms:
                    continue
            except OSError:
                continue
            s = Session(jf, "pi")
            s.cwd = decoded
            try:
                with open(jf, "r", encoding="utf-8") as fh:
                    for lineno, line in enumerate(fh):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            o = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if lineno == 0 or o.get("type") in ("session", "header"):
                            s.cwd = o.get("cwd") or o.get("workingDir") or s.cwd
                            continue
                        inner = o.get("message") if isinstance(o.get("message"), dict) else {}
                        role = inner.get("role") or o.get("role", "")
                        if role not in ("user", "assistant", "human"):
                            continue
                        content = inner.get("content") or o.get("content") \
                            or o.get("text") or ""
                        if isinstance(content, list):
                            parts = []
                            for blk in content:
                                if isinstance(blk, dict) and blk.get("type") == "text":
                                    parts.append(blk.get("text", ""))
                                elif isinstance(blk, str):
                                    parts.append(blk)
                            content = " ".join(p for p in parts if p)
                        content = str(content).strip()
                        if not content:
                            continue
                        ts = normalize_ts(o.get("timestamp") or o.get("createdAt"))
                        if ts > s.last_ts:
                            s.last_ts = ts
                        s.turns.append((f"{role}/text", clip(redact(content), max_chars)))
            except (OSError, IOError):
                continue
            if s.cwd and cwd_matches(repo, s.cwd) and s.turns:
                sessions.append(s)
    return sessions


# --------------------------------------------------------------------------- #
# Main                                                                         #
# --------------------------------------------------------------------------- #

READERS = {
    "claude": read_claude_sessions,
    "codex": read_codex_sessions,
    "pi": read_pi_sessions,
}


def parse_args():
    p = argparse.ArgumentParser(
        description="Read the most recent agent session(s) matching the current repo."
    )
    p.add_argument("--repo", default=None,
                   help="Repo root to match (default: git toplevel of cwd).")
    p.add_argument("--tool", default="all",
                   choices=["all", "claude", "codex", "pi"],
                   help="Which session store(s) to search (default: all).")
    p.add_argument("--count", type=int, default=1,
                   help="How many recent sessions to print (default: 1).")
    p.add_argument("--max-chars", type=int, default=4000,
                   help="Truncate each turn to N chars (default: 4000).")
    p.add_argument("--days", type=int, default=30,
                   help="Ignore sessions older than N days (default: 30).")
    p.add_argument("--include-tools", action="store_true",
                   help="Include tool_use/tool_result one-liners.")
    p.add_argument("--include-subagents", action="store_true",
                   help="Include Claude Code subagent sidechain transcripts "
                        "(off by default; they are not the human-stated WHY).")
    p.add_argument("--list", action="store_true",
                   help="List matching sessions only; do not print transcripts.")
    return p.parse_args()


def main():
    args = parse_args()
    repo = resolve_repo(args.repo)
    cutoff_ms = int((time.time() - args.days * 86400) * 1000)

    tools = list(READERS) if args.tool == "all" else [args.tool]
    sessions = []
    for t in tools:
        try:
            if t == "claude":
                sessions.extend(read_claude_sessions(
                    repo, cutoff_ms, args.include_tools, args.max_chars,
                    include_subagents=args.include_subagents))
            else:
                sessions.extend(READERS[t](repo, cutoff_ms, args.include_tools,
                                           args.max_chars))
        except Exception as e:  # one bad store shouldn't kill the run
            print(f"WARN: {t} reader failed: {e}", file=sys.stderr)

    if not sessions:
        print(f"No recent agent sessions found for repo: {repo}", file=sys.stderr)
        print("(Checked: " + ", ".join(tools) + f"; last {args.days} days.)",
              file=sys.stderr)
        sys.exit(2)

    sessions.sort(key=lambda s: s.sort_key(), reverse=True)
    chosen = sessions[: args.count]

    print(f"# Recent sessions for repo: {repo}")
    print(f"# Matched {len(sessions)} session(s); showing {len(chosen)} newest.\n")

    for i, s in enumerate(chosen, 1):
        when = datetime.fromtimestamp(s.sort_key() / 1000, tz=timezone.utc)
        header = (f"## Session {i}/{len(chosen)}  [{s.tool}]  "
                  f"branch={s.branch or '?'}  "
                  f"{when.strftime('%Y-%m-%d %H:%M UTC')}")
        print(header)
        print(f"# file: {s.path}")
        print(f"# cwd:  {s.cwd}\n")
        if args.list:
            print()
            continue
        for label, text in s.turns:
            print(f"[{label}]")
            print(text)
            print()
        print("-" * 72 + "\n")


if __name__ == "__main__":
    main()
