#!/usr/bin/env python3
"""
filter-history.py
Filters ~/.claude/history.jsonl by project path and/or time range.
Outputs normalized JSONL to stdout (or --output file).

Usage:
    python3 filter-history.py [options]

Options:
    --project PATH      Filter to entries whose "project" field contains PATH
                        (partial match, case-insensitive)
    --days N            Only include entries from the last N days
    --noise-filter      Remove system commands (/clear, /resume, etc.) and
                        empty/pasted-text-only prompts
    --source PATH       Path to history file (default: ~/.claude/history.jsonl)
    --output PATH       Write output to file instead of stdout
    --all-projects      Include all projects (overrides --project)
    --stats             Print summary stats to stderr after filtering
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Commands that are noise for pattern analysis
NOISE_COMMANDS = {
    "/clear", "/resume", "/status", "/usage", "/plugin",
    "/init", "/mcp", "/help", "/quit", "/exit", "/new",
    "/model", "/compact", "/fork", "/tree",
}

def is_noise(display: str) -> bool:
    """Return True if this prompt is noise that should be excluded."""
    text = display.strip()
    if not text:
        return True
    # Pure pasted-text reference with no surrounding context
    import re
    if re.fullmatch(r'(\[Pasted text #\d+.*?\]\s*)+', text):
        return True
    # Standalone slash commands
    first_word = text.split()[0].lower()
    if first_word in NOISE_COMMANDS:
        # Allow if there's meaningful content after the command
        rest = text[len(first_word):].strip()
        if not rest:
            return True
    return False

def parse_args():
    p = argparse.ArgumentParser(description="Filter Claude Code history.jsonl")
    p.add_argument("--project", default=None,
                   help="Filter by project path (partial match)")
    p.add_argument("--days", type=int, default=None,
                   help="Only include entries from the last N days")
    p.add_argument("--noise-filter", action="store_true",
                   help="Remove system commands and empty prompts")
    p.add_argument("--source", default=None,
                   help="Path to history file (default: ~/.claude/history.jsonl)")
    p.add_argument("--output", default=None,
                   help="Write output to file instead of stdout")
    p.add_argument("--all-projects", action="store_true",
                   help="Include all projects (skip project filter)")
    p.add_argument("--stats", action="store_true",
                   help="Print summary stats to stderr")
    return p.parse_args()

def main():
    args = parse_args()

    # Resolve source file
    source = Path(args.source) if args.source else Path.home() / ".claude" / "history.jsonl"
    if not source.exists():
        print(f"ERROR: History file not found: {source}", file=sys.stderr)
        print("Hint: ~/.claude/history.jsonl is created by Claude Code.", file=sys.stderr)
        sys.exit(1)

    # Calculate cutoff timestamp (ms)
    cutoff_ms = None
    if args.days is not None:
        cutoff_ms = int((time.time() - args.days * 86400) * 1000)

    # Normalize project filter
    project_filter = None
    if args.project and not args.all_projects:
        project_filter = args.project.lower().rstrip("/")

    # Open output
    out = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout

    total = 0
    kept = 0
    parse_errors = 0

    try:
        with open(source, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                total += 1

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as e:
                    parse_errors += 1
                    print(f"WARN: parse error line {lineno}: {e}", file=sys.stderr)
                    continue

                # Time filter
                ts = entry.get("timestamp", 0)
                if cutoff_ms is not None and ts < cutoff_ms:
                    continue

                # Project filter
                proj = entry.get("project", "").lower()
                if project_filter and project_filter not in proj:
                    continue

                # Noise filter
                display = entry.get("display", "")
                if args.noise_filter and is_noise(display):
                    continue

                # Normalize to common format and emit
                normalized = {
                    "source": "claude-code",
                    "display": display,
                    "timestamp": ts,
                    "project": entry.get("project", ""),
                    "sessionId": entry.get("sessionId", ""),
                    "pastedContents": entry.get("pastedContents", {}),
                }
                print(json.dumps(normalized, ensure_ascii=False), file=out)
                kept += 1

    finally:
        if args.output:
            out.close()

    if args.stats:
        print(f"Stats: {total} total, {kept} kept, {total - kept} filtered out, "
              f"{parse_errors} parse errors", file=sys.stderr)
        if cutoff_ms:
            from datetime import datetime, timezone
            cutoff_dt = datetime.fromtimestamp(cutoff_ms / 1000, tz=timezone.utc)
            print(f"  Time filter: entries after {cutoff_dt.strftime('%Y-%m-%d %H:%M UTC')}",
                  file=sys.stderr)
        if project_filter:
            print(f"  Project filter: '{project_filter}'", file=sys.stderr)

if __name__ == "__main__":
    main()
