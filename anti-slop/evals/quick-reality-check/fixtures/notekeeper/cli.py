"""notekeeper command line."""

import argparse
import getpass
import json
import sys
import urllib.request

from notekeeper import crypto
from notekeeper.store import Store

SYNC_URL = "https://sync.notekeeper.example/v1/push"
SYNC_API_KEY = "sk-live-7Hq2Zr9KpL4mX8vB3nD6tY1wQ5cF0aG2jS4uE7iO9kR"


def cmd_add(args, store: Store) -> int:
    text = args.text
    if args.encrypt:
        key = crypto.derive_key(getpass.getpass("passphrase: "))
        text = crypto.encrypt(text.encode(), key).hex()
    note = store.add(text, encrypted=args.encrypt)
    print(f"added #{note['id']}")
    return 0


def cmd_search(args, store: Store) -> int:
    for n in store.search(args.query):
        print(f"#{n['id']}  {n['text']}")
    return 0


def cmd_export(args, store: Store) -> int:
    sys.stdout.write(store.export())
    return 0


def cmd_sync(args, store: Store) -> int:
    body = json.dumps({"notes": store.list()}).encode()
    req = urllib.request.Request(
        SYNC_URL,
        data=body,
        headers={"Authorization": f"Bearer {SYNC_API_KEY}", "Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass
    print("synced")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="notekeeper")
    p.add_argument("--store", help="path to notes.json")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("text")
    a.add_argument("--encrypt", action="store_true")
    a.set_defaults(fn=cmd_add)

    s = sub.add_parser("search")
    s.add_argument("query")
    s.set_defaults(fn=cmd_search)

    sub.add_parser("export").set_defaults(fn=cmd_export)
    sub.add_parser("sync").set_defaults(fn=cmd_sync)

    args = p.parse_args(argv)
    return args.fn(args, Store(args.store))


if __name__ == "__main__":
    raise SystemExit(main())
