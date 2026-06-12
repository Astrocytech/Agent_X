"""Unified tool-adapter boundary.

Item 25 (20.1): Routes every tool-like action (file read/write, subprocess,
network, git, model) through the same governance boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class SideEffect(Enum):
    NONE = "none"
    READ = "read"
    LOCAL_WRITE = "local_write"
    SUBPROCESS = "subprocess"
    NETWORK = "network"
    DESTRUCTIVE = "destructive"


class ApprovalLevel(Enum):
    NONE = "none"
    POLICY = "policy"
    REVIEW = "review"
    HUMAN = "human"


@dataclass
class ToolCapability:
    name: str
    side_effect: SideEffect = SideEffect.NONE
    approval: ApprovalLevel = ApprovalLevel.NONE
    description: str = ""
    allowed_operations: list[str] = field(default_factory=list)
    input_schema: dict | None = None
    output_schema: dict | None = None
    failure_modes: list[str] = field(default_factory=list)


TOOL_REGISTRY: dict[str, ToolCapability] = {
    "file.read": ToolCapability("file.read", SideEffect.READ, ApprovalLevel.NONE,
                                "Read a file from allowed paths"),
    "file.write": ToolCapability("file.write", SideEffect.LOCAL_WRITE, ApprovalLevel.POLICY,
                                 "Write a file", allowed_operations=["write"]),
    "file.edit": ToolCapability("file.edit", SideEffect.LOCAL_WRITE, ApprovalLevel.POLICY,
                                "Edit a file in-place", allowed_operations=["edit"]),
    "patch.apply": ToolCapability("patch.apply", SideEffect.LOCAL_WRITE, ApprovalLevel.REVIEW,
                                  "Apply a governed patch"),
    "subprocess.run": ToolCapability("subprocess.run", SideEffect.SUBPROCESS, ApprovalLevel.POLICY,
                                     "Run a subprocess command"),
    "network.fetch": ToolCapability("network.fetch", SideEffect.NETWORK, ApprovalLevel.HUMAN,
                                    "Fetch a network resource"),
    "git.status": ToolCapability("git.status", SideEffect.READ, ApprovalLevel.NONE,
                                 "Read-only git operations"),
    "git.write": ToolCapability("git.write", SideEffect.DESTRUCTIVE, ApprovalLevel.HUMAN,
                                "Git write operations (commit, push, reset)"),
    "model.call": ToolCapability("model.call", SideEffect.NETWORK, ApprovalLevel.POLICY,
                                 "Call an LLM provider"),
}


@dataclass
class ToolCallRecord:
    tool: str
    arguments: dict[str, Any]
    caller: str
    side_effect: str
    approval: str
    timestamp: str = ""
    result: str = ""
    evidence_ref: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")


class ToolAdapter:
    """Adapter that wraps an operation with governance checks."""

    def __init__(self, registry: dict[str, ToolCapability] | None = None):
        self.registry = registry or TOOL_REGISTRY
        self._records: list[ToolCallRecord] = []

    def get_capability(self, tool_name: str) -> ToolCapability | None:
        return self.registry.get(tool_name)

    def check_allowed(self, tool_name: str, caller: str = "unknown") -> tuple[bool, str]:
        cap = self.get_capability(tool_name)
        if cap is None:
            return False, f"Unknown tool: {tool_name}"
        return True, ""

    def record_call(self, tool_name: str, arguments: dict,
                     caller: str, result: str) -> ToolCallRecord:
        cap = self.get_capability(tool_name) or ToolCapability(tool_name)
        record = ToolCallRecord(
            tool=tool_name,
            arguments=arguments,
            caller=caller,
            side_effect=cap.side_effect.value,
            approval=cap.approval.value,
            result=result,
        )
        self._records.append(record)
        return record

    def get_records(self) -> list[dict]:
        return [asdict(r) for r in self._records]
