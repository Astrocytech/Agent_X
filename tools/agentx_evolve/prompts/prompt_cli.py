from __future__ import annotations

import argparse
import sys
from typing import Any

__all__ = [
    "main",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prompt-cli", description="Prompt management CLI")
    parser.add_argument("--validate", type=str, default="", help="Validate a prompt file")
    parser.add_argument("--bind", type=str, default="", help="Bind a prompt contract")
    parser.add_argument("--list", action="store_true", help="List registered prompts")
    parser.add_argument("--diff", type=str, nargs=2, default=None, metavar=("FROM", "TO"), help="Diff two prompt versions")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.validate:
        print("error: --validate is not available (stub)")
        return 1
    if args.bind:
        print("error: --bind is not available (stub)")
        return 1
    if args.list:
        print("error: --list is not available (stub)")
        return 1
    if args.diff:
        print("error: --diff is not available (stub)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
