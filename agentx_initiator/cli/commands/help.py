from __future__ import annotations
from agentx_initiator.cli.registry import list_active, list_reserved


def register(sub):
    p = sub.add_parser("help", help="Show available commands")
    p.set_defaults(func=run)


def run(args):
    print("Available commands:")
    for cmd in list_active():
        print(f"  {cmd.name:<12} {cmd.description}")
    reserved = list_reserved()
    if reserved:
        print("\nReserved commands (not implemented in Product Milestone 1):")
        for cmd in reserved:
            print(f"  {cmd.name:<12} {cmd.description}")
