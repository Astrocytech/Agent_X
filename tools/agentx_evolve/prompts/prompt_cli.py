from __future__ import annotations
import argparse
import sys
from typing import Any

try:
    from agentx_evolve.prompts import cli as _cli

    _HAS_CLI = True
except ImportError:
    _HAS_CLI = False

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
        print(f"validate: {args.validate} (stub)")
    if args.bind:
        print(f"bind: {args.bind} (stub)")
    if args.list:
        print("list: (stub)")
    if args.diff:
        print(f"diff: {args.diff[0]} -> {args.diff[1]} (stub)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
