from __future__ import annotations

import json
import os
from hashlib import sha256
from pathlib import Path
from typing import Any

from agentx_evolve.adapters.tool_adapter import ToolAdapter
from agentx_evolve.adapters.tool_result import ToolCall, ToolResult

LOCAL_TOOL_ADAPTER_ID = "local_read_only"
ALLOWED_TOOLS = {"read_repo_info", "list_repo_files", "read_file_content"}


def _hash(data: str) -> str:
    return sha256(data.encode("utf-8")).hexdigest()


def _is_within_repo(path: str, repo_root: str | None = None) -> bool:
    resolved = Path(path).resolve()
    root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    try:
        resolved.relative_to(root)
        return True
    except ValueError:
        return False


class LocalToolAdapter(ToolAdapter):
    def __init__(self, repo_root: str | None = None):
        self._repo_root = repo_root or os.getcwd()

    def describe_capabilities(self) -> dict[str, Any]:
        return {
            "adapter_id": LOCAL_TOOL_ADAPTER_ID,
            "allowed_tools": sorted(ALLOWED_TOOLS),
            "read_only": True,
            "offline": True,
            "deterministic": True,
        }

    def validate_call(self, call: dict[str, Any]) -> dict[str, Any]:
        errors: list[str] = []
        tool_name = call.get("tool_name", "")
        if tool_name not in ALLOWED_TOOLS:
            errors.append(f"unknown tool: {tool_name}")
        if not call.get("call_id"):
            errors.append("call_id is required")
        if not call.get("run_id"):
            errors.append("run_id is required")
        return {"valid": len(errors) == 0, "errors": errors}

    def simulate_call(self, call: dict[str, Any]) -> dict[str, Any]:
        return self.execute_call(call)

    def execute_call(self, call: dict[str, Any]) -> dict[str, Any]:
        tool_name = call.get("tool_name", "")
        args = call.get("arguments", {})
        call_id = call.get("call_id", "unknown")

        if tool_name == "read_repo_info":
            return self._read_repo_info(args, call_id)
        if tool_name == "list_repo_files":
            return self._list_repo_files(args, call_id)
        if tool_name == "read_file_content":
            return self._read_file_content(args, call_id)

        return ToolResult(
            tool_name=tool_name, call_id=call_id, status="DENIED",
            failure_class="capability_mismatch",
            failure_reason=f"unknown tool: {tool_name}",
            provenance={"adapter_id": LOCAL_TOOL_ADAPTER_ID},
        ).to_dict()

    def normalize_result(self, result: dict[str, Any]) -> dict[str, Any]:
        return {
            "tool_name": result.get("tool_name", ""),
            "call_id": result.get("call_id", ""),
            "status": result.get("status", "DENIED"),
            "output_hash": result.get("output_hash", ""),
            "output": result.get("output", {}),
            "provenance": result.get("provenance", {}),
        }

    def _read_repo_info(self, args: dict[str, Any], call_id: str) -> dict[str, Any]:
        path = args.get("path", ".")
        target = Path(self._repo_root) / path
        if not _is_within_repo(str(target), self._repo_root):
            return ToolResult(
                tool_name="read_repo_info", call_id=call_id, status="DENIED",
                failure_class="context_contamination",
                failure_reason="path traversal blocked",
                provenance={"adapter_id": LOCAL_TOOL_ADAPTER_ID},
            ).to_dict()

        info = {
            "path": str(target),
            "exists": target.exists(),
            "is_dir": target.is_dir() if target.exists() else False,
            "name": target.name,
        }
        if target.exists() and target.is_dir():
            entries = sorted(target.iterdir())[:50]
            info["entries"] = [e.name for e in entries]
        raw = json.dumps(info, sort_keys=True)
        return ToolResult(
            tool_name="read_repo_info", call_id=call_id, status="SUCCESS",
            output=info, output_hash=_hash(raw),
            provenance={"adapter_id": LOCAL_TOOL_ADAPTER_ID, "path": str(target)},
        ).to_dict()

    def _list_repo_files(self, args: dict[str, Any], call_id: str) -> dict[str, Any]:
        pattern = args.get("pattern", "*")
        root = Path(self._repo_root)
        files = [str(p.relative_to(root)) for p in root.rglob(pattern) if p.is_file()][:100]
        raw = json.dumps(files, sort_keys=True)
        return ToolResult(
            tool_name="list_repo_files", call_id=call_id, status="SUCCESS",
            output={"files": files}, output_hash=_hash(raw),
            provenance={"adapter_id": LOCAL_TOOL_ADAPTER_ID},
        ).to_dict()

    def _read_file_content(self, args: dict[str, Any], call_id: str) -> dict[str, Any]:
        file_path = args.get("file_path", "")
        target = Path(self._repo_root) / file_path
        if not _is_within_repo(str(target), self._repo_root):
            return ToolResult(
                tool_name="read_file_content", call_id=call_id, status="DENIED",
                failure_class="context_contamination",
                failure_reason="path traversal blocked",
                provenance={"adapter_id": LOCAL_TOOL_ADAPTER_ID},
            ).to_dict()
        if not target.exists() or not target.is_file():
            return ToolResult(
                tool_name="read_file_content", call_id=call_id, status="DENIED",
                failure_class="tool_execution_error",
                failure_reason="file not found",
                provenance={"adapter_id": LOCAL_TOOL_ADAPTER_ID},
            ).to_dict()
        try:
            content = target.read_text(encoding="utf-8", errors="replace")[:10000]
            raw_hash = _hash(content)
            return ToolResult(
                tool_name="read_file_content", call_id=call_id, status="SUCCESS",
                output={"file_path": file_path, "size": len(content), "content_preview": content[:500]},
                output_hash=raw_hash,
                provenance={"adapter_id": LOCAL_TOOL_ADAPTER_ID, "path": file_path},
            ).to_dict()
        except Exception as e:
            return ToolResult(
                tool_name="read_file_content", call_id=call_id, status="DENIED",
                failure_class="tool_execution_error",
                failure_reason=str(e),
                provenance={"adapter_id": LOCAL_TOOL_ADAPTER_ID},
            ).to_dict()
