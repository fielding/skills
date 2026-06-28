#!/usr/bin/env python3
"""
extract-pi-history.py
Extracts user prompts from pi-mono session files (~/.pi/agent/sessions/)
and outputs normalized JSONL.

pi-mono sessions use a tree structure: each JSONL entry has an "id" and
"parentId" field enabling branching. This script flattens each session to
its user-message entries (type="user" or role="user").

Session path format:
    ~/.pi/agent/sessions/--{encoded-path}--/{timestamp}_{uuid}.jsonl
    where {encoded-path} is the working directory with "/" replaced by "-"

Usage:
    python3 extract-pi-history.py [options]

Options:
    --days N            Only include sessions modified in the last N days
    --project PATH      Filter to sessions from a project path
                        (partial match against decoded directory path)
    --sessions-dir PATH Override sessions directory (default: ~/.pi/agent/sessions)
    --output PATH       Write output to file instead of stdout
    --stats             Print summary stats to stderr
    --include-branches  Include all branch nodes, not just the main trunk.
                        Default: only include the deepest active branch path.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

def get_sessions_dir() -> Path:
    return Path.home() / ".pi" / "agent" / "sessions"

def decode_path(encoded: str) -> str:
    """
    Reverse pi-mono's path encoding:
    directory "--Users-alice-projects-foo--" -> "/Users/alice/projects/foo"
    The outer "--" delimiters are stripped, then "-" is replaced with "/".
    Note: this is imperfect for paths with hyphens in directory names, but
    good enough for filtering purposes.
    """
    # Strip leading/trailing "--" if present
    s = encoded.strip("-")
    # Replace "-" with "/" to approximate the original path
    return "/" + s.replace("-", "/")

def find_session_files(sessions_dir: Path, cutoff_mtime: float | None,
                       project_filter: str | None) -> list[Path]:
    """Walk sessions_dir, returning .jsonl files matching filters."""
    if not sessions_dir.exists():
        return []

    results = []
    for dir_entry in sessions_dir.iterdir():
        if not dir_entry.is_dir():
            continue

        # Check project filter against decoded path
        if project_filter:
            decoded = decode_path(dir_entry.name)
            if project_filter.lower() not in decoded.lower():
                continue

        for f in dir_entry.glob("*.jsonl"):
            if cutoff_mtime and f.stat().st_mtime < cutoff_mtime:
                continue
            results.append(f)

    return results

def extract_user_prompts_from_session(path: Path, cutoff_ms: int | None,
                                      include_branches: bool) -> list[dict]:
    """
    Parse a pi-mono session JSONL file and extract user message entries.

    The file is a sequence of JSON objects. Relevant entry types:
      - Header entry: {"type": "header", "version": ..., "id": ..., ...}
      - Message entries: {"type": "message", "role": "user"|"assistant", ...}
        or {"type": "user", "content": ...}
      - Tool entries, assistant entries, etc.

    Tree structure: each entry has "id" and "parentId" for branching.
    For simplicity we extract ALL user entries unless include_branches=False,
    in which case we follow only the deepest (most recently updated) branch.
    """
    entries = []
    header = {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if lineno == 0 or obj.get("type") in ("session", "header"):
                    header = obj
                    continue
                entries.append(obj)
    except (OSError, IOError) as e:
        print(f"WARN: Could not read {path}: {e}", file=sys.stderr)
        return []

    if not entries:
        return []

    # Determine session metadata from header or first entry
    session_id = header.get("id") or str(path.stem)
    working_dir = header.get("cwd") or header.get("workingDir") or ""

    # If not including all branches, find deepest branch path
    if not include_branches and len(entries) > 1:
        # Build parent->children map
        by_id = {e.get("id"): e for e in entries if e.get("id")}
        # Find leaf nodes (no children)
        children = {e.get("parentId") for e in entries if e.get("parentId")}
        leaves = [e for e in entries if e.get("id") and e.get("id") not in children]
        # Pick the leaf with the latest timestamp
        def entry_ts(e):
            ts = e.get("timestamp") or e.get("createdAt") or 0
            return _normalize_ts(ts)
        if leaves:
            best_leaf = max(leaves, key=entry_ts)
            # Walk back to root to get the trunk path
            trunk_ids = set()
            cur = best_leaf
            while cur:
                eid = cur.get("id")
                if not eid or eid in trunk_ids:
                    break
                trunk_ids.add(eid)
                parent_id = cur.get("parentId")
                cur = by_id.get(parent_id)
            entries = [e for e in entries if e.get("id") in trunk_ids]

    # Extract user messages
    messages = []
    for entry in entries:
        entry_type = entry.get("type", "")
        # Current pi (version 3) nests the chat payload under "message":
        #   {"type": "message", "id": ..., "parentId": ...,
        #    "message": {"role": "user", "content": [{"type":"text","text":...}]}}
        # Older formats put role/content at the top level, so fall back.
        inner = entry.get("message") if isinstance(entry.get("message"), dict) else {}
        role = inner.get("role") or entry.get("role", "")

        is_user = (
            entry_type in ("user",)
            or role in ("user", "human")
            or (entry_type == "message" and role in ("user", "human"))
        )
        if not is_user:
            continue

        # Extract text content (nested under message.content in v3)
        content = (
            inner.get("content")
            or entry.get("content")
            or entry.get("text")
            or (entry.get("message") if not inner else None)
            or ""
        )
        if isinstance(content, list):
            # Content blocks format: [{"type": "text", "text": "..."}, ...]
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif isinstance(block, str):
                    parts.append(block)
            content = " ".join(p for p in parts if p).strip()
        elif not isinstance(content, str):
            content = str(content)

        content = content.strip()
        if not content:
            continue

        ts = _normalize_ts(entry.get("timestamp") or entry.get("createdAt") or 0)
        if cutoff_ms and ts < cutoff_ms:
            continue

        messages.append({
            "source": "pi",
            "display": content,
            "timestamp": ts,
            "project": working_dir,
            "sessionId": session_id,
        })

    return messages

def _normalize_ts(ts) -> int:
    """Normalize timestamp to milliseconds."""
    if not ts:
        return 0
    if isinstance(ts, str):
        try:
            from datetime import datetime, timezone
            dt = datetime.fromisoformat(ts.rstrip("Z"))
            return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
        except Exception:
            return 0
    val = int(ts)
    # Seconds -> ms if looks like seconds
    if val < 32503680000:
        return val * 1000
    return val

def parse_args():
    p = argparse.ArgumentParser(
        description="Extract pi-mono session history to normalized JSONL"
    )
    p.add_argument("--days", type=int, default=None,
                   help="Only include sessions modified in the last N days")
    p.add_argument("--project", default=None,
                   help="Filter to sessions from a project path (partial match)")
    p.add_argument("--sessions-dir", default=None,
                   help="Override sessions directory (default: ~/.pi/agent/sessions)")
    p.add_argument("--output", default=None,
                   help="Write output to file instead of stdout")
    p.add_argument("--stats", action="store_true",
                   help="Print summary stats to stderr")
    p.add_argument("--include-branches", action="store_true",
                   help="Include all branch nodes, not just the active trunk")
    return p.parse_args()

def main():
    args = parse_args()

    sessions_dir = (Path(args.sessions_dir) if args.sessions_dir
                    else get_sessions_dir())

    if not sessions_dir.exists():
        print(f"ERROR: pi sessions directory not found: {sessions_dir}", file=sys.stderr)
        print("Is pi-mono installed and has it been run at least once?", file=sys.stderr)
        sys.exit(1)

    cutoff_mtime = None
    cutoff_ms = None
    if args.days is not None:
        cutoff_mtime = time.time() - args.days * 86400
        cutoff_ms = int(cutoff_mtime * 1000)

    project_filter = args.project

    session_files = find_session_files(sessions_dir, cutoff_mtime, project_filter)

    if args.stats:
        print(f"Found {len(session_files)} session file(s) matching filters",
              file=sys.stderr)

    all_messages = []
    for sf in sorted(session_files):
        msgs = extract_user_prompts_from_session(sf, cutoff_ms, args.include_branches)
        all_messages.extend(msgs)

    # Sort by timestamp
    all_messages.sort(key=lambda m: m["timestamp"])

    # Output
    out = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    try:
        for msg in all_messages:
            print(json.dumps(msg, ensure_ascii=False), file=out)
    finally:
        if args.output:
            out.close()

    if args.stats:
        print(f"Extracted {len(all_messages)} user messages from pi-mono",
              file=sys.stderr)
        if cutoff_ms:
            from datetime import datetime, timezone
            dt = datetime.fromtimestamp(cutoff_ms / 1000, tz=timezone.utc)
            print(f"  Time filter: after {dt.strftime('%Y-%m-%d %H:%M UTC')}",
                  file=sys.stderr)
        if project_filter:
            print(f"  Project filter: '{project_filter}'", file=sys.stderr)

if __name__ == "__main__":
    main()
