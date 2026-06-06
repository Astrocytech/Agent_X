from __future__ import annotations

import argparse

__all__ = [
    "main",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Human Review CLI")
    parser.add_argument("--approve", type=str, default="", help="Approval ID to approve")
    parser.add_argument("--reject", type=str, default="", help="Approval ID to reject")
    parser.add_argument("--list", action="store_true", help="List pending reviews")
    args = parser.parse_args()

    if args.approve:
        ...  # approve logic
    elif args.reject:
        ...  # reject logic
    elif args.list:
        ...  # list logic
    else:
        parser.print_help()
