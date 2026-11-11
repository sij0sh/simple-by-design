#!/usr/bin/env python3
"""JSON-in/JSON-out adapter. Run from the task's project, not the skill directory."""

import argparse
import json
from pathlib import Path
import sys

from engine import ledger
from engine.state import Store, decode


def parser():
    result = argparse.ArgumentParser(description="Persistent adaptive solution-design ledger (no scheduler)")
    result.add_argument("--root", type=Path, default=Path.cwd(), help="task project directory (default: cwd)")
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("new", "show", "record", "finish"):
        command = commands.add_parser(name)
        command.add_argument("task", help="stable task ID; no paths")
        if name in {"record", "finish"}:
            command.add_argument("--at", type=int, required=True, help="expected current revision")
        if name == "show":
            command.add_argument("--at", type=int, help="reproduce a historical snapshot")
            command.add_argument("--history", action="store_true", help="include event history through that revision")
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    store = Store(args.root / ".agents" / "sbd-adaptive")
    try:
        if args.command == "show":
            view = store.show(args.task, at=args.at, history=args.history)
        else:
            data = decode(sys.stdin.read())
            if args.command == "new":
                view = store.new(args.task, data)
            else:
                view = store.record(args.task, data, at=args.at, finish=args.command == "finish")
        print(json.dumps(view, ensure_ascii=False, allow_nan=False, indent=2))
        return 0
    except (ledger.LedgerError, OSError, UnicodeError, RecursionError) as error:
        print(f"sbd: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
