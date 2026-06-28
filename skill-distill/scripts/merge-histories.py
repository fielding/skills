#!/usr/bin/env python3
"""
merge-histories.py
Merges normalized JSONL output from multiple history extractors into a
single, deduplicated, chronologically sorted stream.

This is a convenience wrapper that runs all available extractors and
merges their output. You can also pipe extractor outputs into it.

Usage:
    # Run all extractors and merge:
    python3 merge-histories.py --days 30 [--project PATH] [--output FILE]

    # Merge pre-generated files:
    python3 merge-histories.py --input claude.jsonl codex.jsonl pi.jsonl cursor.jsonl

    # Pipe input:
    python3 filter-history.py --days 30 | python3 merge-histories.py --stdin

Options:
    --days N            Pass to all extractors (last N days)
    --project PATH      Pass to all extractors (project filter)
    --sources LIST      Comma-separated subset of: claude,codex,pi,cursor
                        Default: all available
    --input FILES       One or more pre-generated JSONL files to merge
    --stdin             Read additional JSONL from stdin
    --output PATH       Write merged output to file instead of stdout
    --stats             Print per-source counts to stderr
    --skill-dir PATH    Directory containing this scripts/ folder
                        (default: parent of this script's directory)
    --noise-filter      Apply noise filtering to all sources
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SOURCES = ["claude", "codex", "pi", "cursor"]

def find_script(name: str, scripts_dir: Path) -> Path | None:
    p = scripts_dir / name
    return p if p.exists() else None

def run_extractor(cmd: list[str]) -> list[dict]:
    """Run an extractor subprocess and return parsed JSONL entries."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode != 0 and result.stderr:
            print(f"WARN: {cmd[2]} stderr: {result.stderr.strip()}", file=sys.stderr)
        messages = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        return messages
    except FileNotFoundError:
        print(f"WARN: python3 not found or script missing: {cmd}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"WARN: Error running {cmd}: {e}", file=sys.stderr)
        return []

def read_jsonl_file(path: Path) -> list[dict]:
    messages = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    except (OSError, IOError) as e:
        print(f"WARN: Could not read {path}: {e}", file=sys.stderr)
    return messages

def read_stdin() -> list[dict]:
    messages = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return messages

def parse_args():
    p = argparse.ArgumentParser(
        description="Merge normalized JSONL from all AI history sources"
    )
    p.add_argument("--days", type=int, default=30,
                   help="Pass --days to all extractors (default: 30)")
    p.add_argument("--project", default=None,
                   help="Pass --project to all extractors")
    p.add_argument("--sources", default=None,
                   help="Comma-separated subset: claude,codex,pi,cursor")
    p.add_argument("--input", nargs="+", default=None,
                   help="Pre-generated JSONL files to merge instead of running extractors")
    p.add_argument("--stdin", action="store_true",
                   help="Also read JSONL from stdin")
    p.add_argument("--output", default=None,
                   help="Write output to file instead of stdout")
    p.add_argument("--stats", action="store_true",
                   help="Print per-source counts to stderr")
    p.add_argument("--skill-dir", default=None,
                   help="Root directory of this skill (default: auto-detected)")
    p.add_argument("--noise-filter", action="store_true",
                   help="Apply noise filtering to Claude Code source")
    return p.parse_args()

def main():
    args = parse_args()

    # Resolve scripts dir
    scripts_dir = Path(__file__).parent
    skill_dir = Path(args.skill_dir) if args.skill_dir else scripts_dir.parent

    active_sources = SOURCES
    if args.sources:
        active_sources = [s.strip().lower() for s in args.sources.split(",")]
        invalid = [s for s in active_sources if s not in SOURCES]
        if invalid:
            print(f"WARN: Unknown sources: {invalid}. Valid: {SOURCES}", file=sys.stderr)
        active_sources = [s for s in active_sources if s in SOURCES]

    all_messages: list[dict] = []
    source_counts: dict[str, int] = {}

    if args.input:
        # Merge from pre-generated files
        for f in args.input:
            msgs = read_jsonl_file(Path(f))
            all_messages.extend(msgs)
            source = msgs[0]["source"] if msgs else Path(f).stem
            source_counts[source] = source_counts.get(source, 0) + len(msgs)
    else:
        # Run extractors. Each is an independent, I/O-bound subprocess, so we
        # build the command list and run them concurrently in a thread pool
        # instead of one after another (the serial path took >6 min).
        python = sys.executable

        common_args = []
        if args.days:
            common_args += ["--days", str(args.days)]
        if args.project:
            common_args += ["--project", args.project]

        # (count_key, script_name, extra_args, missing_warning)
        extractor_specs = [
            ("claude-code", "filter-history.py",
             ["--noise-filter"] if args.noise_filter else [],
             "filter-history.py not found, skipping Claude Code"),
            ("codex", "extract-codex-history.py",
             # --full-transcripts is the current source of truth (the
             # history.jsonl index is stale); pass it explicitly so behavior is
             # stable even if the extractor default ever changes.
             ["--full-transcripts"],
             "extract-codex-history.py not found, skipping Codex"),
            ("pi", "extract-pi-history.py", [],
             "extract-pi-history.py not found, skipping pi-mono"),
            ("cursor", "extract-cursor-history.py", [],
             "extract-cursor-history.py not found, skipping Cursor"),
        ]
        source_keys = {
            "claude-code": "claude", "codex": "codex",
            "pi": "pi", "cursor": "cursor",
        }

        jobs = []  # (count_key, cmd)
        for count_key, script_name, extra, missing_msg in extractor_specs:
            if source_keys[count_key] not in active_sources:
                continue
            script = find_script(script_name, scripts_dir)
            if not script:
                print(f"WARN: {missing_msg}", file=sys.stderr)
                continue
            jobs.append((count_key, [python, str(script)] + extra + common_args))

        from concurrent.futures import ThreadPoolExecutor
        if jobs:
            with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
                results = list(pool.map(lambda j: (j[0], run_extractor(j[1])), jobs))
            for count_key, msgs in results:
                all_messages.extend(msgs)
                source_counts[count_key] = len(msgs)

    # Read stdin if requested
    if args.stdin:
        stdin_msgs = read_stdin()
        all_messages.extend(stdin_msgs)
        source_counts["stdin"] = len(stdin_msgs)

    # Deduplicate: same source + sessionId + first 80 chars of display
    seen = set()
    deduped = []
    for m in all_messages:
        key = (m.get("source", ""), m.get("sessionId", ""), m.get("display", "")[:80])
        if key not in seen:
            seen.add(key)
            deduped.append(m)

    # Sort chronologically
    deduped.sort(key=lambda m: m.get("timestamp", 0))

    # Output
    out = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    try:
        for msg in deduped:
            print(json.dumps(msg, ensure_ascii=False), file=out)
    finally:
        if args.output:
            out.close()

    if args.stats:
        print("\nMerge summary:", file=sys.stderr)
        for source, count in sorted(source_counts.items()):
            print(f"  {source:20s}: {count:4d} messages", file=sys.stderr)
        print(f"  {'TOTAL (deduped)':20s}: {len(deduped):4d} messages", file=sys.stderr)

if __name__ == "__main__":
    main()
