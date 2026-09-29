import argparse
import sys

from fetchkit.fetch import get


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="fetchkit")
    parser.add_argument("url")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args(argv)
    sys.stdout.buffer.write(get(args.url, timeout=args.timeout))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
