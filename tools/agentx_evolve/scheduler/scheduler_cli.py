from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agentx_evolve.scheduler.scheduler_dispatcher import SchedulerDispatcher


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scheduler",
        description="AgentX Scheduler CLI",
    )
    parser.add_argument(
        "--runtime-root",
        default=".agentx-init/scheduler",
        help="Runtime root directory for scheduler state",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("start", help="Start a scheduler session")
    start_parser.add_argument("session_id", help="Session identifier")
    start_parser.add_argument("--task-id", default="", help="Optional task to queue on start")

    stop_parser = subparsers.add_parser("stop", help="Stop a scheduler session")
    stop_parser.add_argument("session_id", help="Session identifier")

    status_parser = subparsers.add_parser("status", help="Show scheduler status")
    status_parser.add_argument("--session-id", default="", help="Optional session to inspect")

    task_parser = subparsers.add_parser("task", help="Task operations")
    task_sub = task_parser.add_subparsers(dest="task_command", required=True)

    task_create_parser = task_sub.add_parser("create", help="Create a new task")
    task_create_parser.add_argument("task_id", help="Task identifier")
    task_create_parser.add_argument("session_id", help="Session identifier")
    task_create_parser.add_argument("--payload-ref", default="", help="Payload reference")
    task_create_parser.add_argument("--priority", type=int, default=50, help="Task priority")
    task_create_parser.add_argument("--dependency-ids", nargs="*", default=[], help="Dependency task IDs")

    task_get_parser = task_sub.add_parser("get", help="Get task details")
    task_get_parser.add_argument("task_id", help="Task identifier")

    return parser


def cmd_start(args: argparse.Namespace) -> int:
    dispatcher = SchedulerDispatcher(runtime_root=args.runtime_root)
    dispatcher.initialize()
    if args.task_id:
        result = dispatcher.create_task(args.task_id, args.session_id)
    else:
        result = {"status": "SESSION_ACTIVE", "session_id": args.session_id}
    print(result)
    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    print({"status": "SESSION_STOPPED", "session_id": args.session_id})
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    dispatcher = SchedulerDispatcher(runtime_root=args.runtime_root)
    if args.session_id:
        sessions = dispatcher.get_active_sessions()
        found = [s for s in sessions if s.session_id == args.session_id]
        result = {
            "session_id": args.session_id,
            "active": len(found) > 0,
            "sessions": [s.__dict__ if hasattr(s, "__dict__") else str(s) for s in found],
        }
    else:
        queue = dispatcher.get_queue_state()
        sessions = dispatcher.get_active_sessions()
        result = {
            "queue": queue.__dict__ if hasattr(queue, "__dict__") else str(queue),
            "active_sessions": len(sessions),
            "sessions": [s.__dict__ if hasattr(s, "__dict__") else str(s) for s in sessions],
        }
    print(result)
    return 0


def cmd_task(args: argparse.Namespace) -> int:
    dispatcher = SchedulerDispatcher(runtime_root=args.runtime_root)
    if args.task_command == "create":
        result = dispatcher.create_task(
            args.task_id,
            args.session_id,
            payload_ref=args.payload_ref,
            priority=args.priority,
            dependency_ids=args.dependency_ids,
        )
    elif args.task_command == "get":
        task = dispatcher.get_task(args.task_id)
        result = task.__dict__ if task else {"status": "NOT_FOUND", "task_id": args.task_id}
    else:
        result = {"status": "UNKNOWN_COMMAND"}
    print(result)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "start":
        return cmd_start(args)
    elif args.command == "stop":
        return cmd_stop(args)
    elif args.command == "status":
        return cmd_status(args)
    elif args.command == "task":
        return cmd_task(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
