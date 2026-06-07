from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ALLOWED_ACTION_TYPES = {"patch", "validate", "report", "noop"}
ALLOWED_PATCH_FORMATS = {"unified_diff"}

BLOCKED_COMMAND_PATTERNS = [
    "rm -rf", "sudo", "curl | sh", "wget | sh",
    "chmod -R 777", "chown", "mkfs", "dd",
]

ALLOWED_VALIDATION_COMMANDS = [
    "python -m compileall tools/agentx_evolve",
    "python -m tools.agentx_evolve --help",
    "python -m tools.agentx_evolve chat --once \"Say READY\" --mock --json",
    "pytest tools/agentx_evolve/tests -q",
]


class PlanParseError(Exception):
    def __init__(self, message: str, reason: str = "malformed plan"):
        self.reason = reason
        super().__init__(message)


class StructuredPlanParser:
    def parse(self, raw: str | dict[str, Any]) -> dict[str, Any]:
        if isinstance(raw, str):
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                raise PlanParseError(f"malformed JSON: {e}")
        else:
            data = raw

        self._validate_schema_version(data)
        self._validate_summary(data)
        self._validate_actions(data)
        self._validate_patches(data)
        self._validate_commands(data)
        return data

    @staticmethod
    def _validate_schema_version(data: dict[str, Any]) -> None:
        if "schema_version" not in data:
            raise PlanParseError("missing schema_version")
        if data["schema_version"] != "agentx.structured_plan.v1":
            raise PlanParseError(
                f"unknown schema_version: {data['schema_version']}",
            )

    @staticmethod
    def _validate_summary(data: dict[str, Any]) -> None:
        if "summary" not in data or not isinstance(data["summary"], str):
            raise PlanParseError("missing or invalid summary")

    @staticmethod
    def _validate_actions(data: dict[str, Any]) -> None:
        actions = data.get("actions", [])
        if not isinstance(actions, list):
            raise PlanParseError("actions must be a list")
        for i, action in enumerate(actions):
            if not isinstance(action, dict):
                raise PlanParseError(f"action[{i}] must be an object")
            atype = action.get("type", "")
            if atype not in ALLOWED_ACTION_TYPES:
                raise PlanParseError(
                    f"action[{i}]: unknown type '{atype}'",
                )
            desc = action.get("description", "")
            if not isinstance(desc, str) or not desc:
                raise PlanParseError(
                    f"action[{i}]: missing or invalid description",
                )
            target = action.get("target", "")
            if target:
                _validate_target(target)

    @staticmethod
    def _validate_patches(data: dict[str, Any]) -> None:
        patches = data.get("patches", [])
        if not isinstance(patches, list):
            raise PlanParseError("patches must be a list")
        for i, patch in enumerate(patches):
            if not isinstance(patch, dict):
                raise PlanParseError(f"patch[{i}] must be an object")
            fmt = patch.get("format", "")
            if fmt not in ALLOWED_PATCH_FORMATS:
                raise PlanParseError(
                    f"patch[{i}]: unknown format '{fmt}'",
                )
            content = patch.get("content", "")
            if not isinstance(content, str) or not content:
                raise PlanParseError(
                    f"patch[{i}]: missing or empty content",
                )
            if "diff --git" not in content and "---" not in content:
                raise PlanParseError(
                    f"patch[{i}]: does not look like unified diff",
                )

    @staticmethod
    def _validate_commands(data: dict[str, Any]) -> None:
        commands = data.get("validation_commands", [])
        if not isinstance(commands, list):
            raise PlanParseError("validation_commands must be a list")
        for i, cmd in enumerate(commands):
            if not isinstance(cmd, str):
                raise PlanParseError(f"validation_commands[{i}] must be a string")
            _validate_allowed_command(cmd)


def _validate_target(target: str) -> None:
    if target.startswith("/"):
        raise PlanParseError(f"absolute path target: {target}")
    parts = target.split("/")
    if ".." in parts:
        raise PlanParseError(f"path traversal in target: {target}")



def _validate_allowed_command(cmd: str) -> None:
    for blocked in BLOCKED_COMMAND_PATTERNS:
        if blocked in cmd:
            raise PlanParseError(
                f"blocked command pattern '{blocked}' in: {cmd}",
                reason="BLOCKED",
            )
