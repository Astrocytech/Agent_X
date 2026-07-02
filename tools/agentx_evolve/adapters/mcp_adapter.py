from __future__ import annotations

import json
import subprocess
from typing import Any

from agentx_evolve.adapters.mcp_contract import (
    MCPDescriptor,
    REAL_TRANSPORTS,
    SUPPORTED_TRANSPORTS,
    TRANSPORT_REQUIRES_NETWORK,
)
from agentx_evolve.adapters.tool_result import ToolResult

MCP_ADAPTER_ID = "mcp_shell"


class MCPTransportRunner:
    def execute(
        self, tool_name: str, server_id: str, transport: str, input_data: dict[str, Any],
    ) -> dict[str, Any]:
        if transport == "local_mock_transport":
            return self._mock_execute(tool_name, server_id, input_data)
        if transport == "stdio":
            return self._stdio_execute(server_id, input_data)
        # network transports are structural-only (quarantined)
        return {
            "tool_name": tool_name,
            "server_id": server_id,
            "output": {"error": f"transport {transport} is structural-only, not executed"},
            "output_hash": "",
            "status": "BLOCKED",
        }

    def _mock_execute(
        self, tool_name: str, server_id: str, input_data: dict[str, Any],
    ) -> dict[str, Any]:
        result = {
            "tool_name": tool_name,
            "server_id": server_id,
            "output": {"mock": True, "input_keys": sorted(input_data.keys())},
            "output_hash": f"mock_{tool_name}_{server_id}",
            "status": "SUCCESS",
        }
        return result

    def _stdio_execute(
        self, server_id: str, input_data: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            proc = subprocess.run(
                [server_id],
                input=json.dumps(input_data),
                capture_output=True,
                text=True,
                timeout=30,
            )
            output: dict[str, Any] = {}
            if proc.stdout:
                output = json.loads(proc.stdout)
            return {
                "tool_name": server_id,
                "server_id": server_id,
                "output": output,
                "output_hash": "",
                "status": "SUCCESS" if proc.returncode == 0 else "EXECUTION_ERROR",
                "stderr": proc.stderr,
            }
        except FileNotFoundError:
            return {
                "tool_name": server_id,
                "server_id": server_id,
                "output": {"error": f"MCP server executable not found: {server_id}"},
                "output_hash": "",
                "status": "EXECUTION_ERROR",
            }
        except subprocess.TimeoutExpired:
            return {
                "tool_name": server_id,
                "server_id": server_id,
                "output": {"error": f"MCP server timed out: {server_id}"},
                "output_hash": "",
                "status": "TIMEOUT",
            }
        except json.JSONDecodeError:
            return {
                "tool_name": server_id,
                "server_id": server_id,
                "output": {"error": "MCP server returned invalid JSON"},
                "output_hash": "",
                "status": "EXECUTION_ERROR",
            }

    def supports_transport(self, transport: str) -> bool:
        if transport == "local_mock_transport":
            return True
        if transport == "stdio":
            return True
        return False


class MCPAdapterShell:
    def __init__(self) -> None:
        self._descriptors: dict[str, MCPDescriptor] = {}
        self._transport_runner = MCPTransportRunner()

    def register_descriptor(self, descriptor: MCPDescriptor) -> None:
        errors = descriptor.validate()
        if errors:
            raise ValueError(f"invalid MCP descriptor: {'; '.join(errors)}")
        self._descriptors[descriptor.tool_name] = descriptor

    def get_descriptor(self, tool_name: str) -> MCPDescriptor | None:
        return self._descriptors.get(tool_name)

    def validate_call(self, server_id: str, tool_name: str, transport: str) -> dict[str, Any]:
        errors: list[str] = []
        desc = self._descriptors.get(tool_name)
        if not desc:
            errors.append(f"unknown MCP tool: {tool_name}")
            return {"valid": False, "errors": errors}
        if desc.server_id != server_id:
            errors.append(f"unknown MCP server: {server_id}")
        if transport not in SUPPORTED_TRANSPORTS:
            errors.append(f"unsupported transport: {transport}")
        if desc.live_required:
            errors.append("live MCP disabled by default")
        return {"valid": len(errors) == 0, "errors": errors}

    def execute_tool(
        self, tool_name: str, server_id: str, transport: str, input_data: dict[str, Any],
    ) -> dict[str, Any]:
        validation = self.validate_call(server_id, tool_name, transport)
        if not validation["valid"]:
            return {
                "tool_name": tool_name,
                "server_id": server_id,
                "output": {"errors": validation["errors"]},
                "output_hash": "",
                "status": "BLOCKED",
            }
        return self._transport_runner.execute(tool_name, server_id, transport, input_data)

    def normalize_result(self, result: dict[str, Any]) -> dict[str, Any]:
        normalized = {
            "tool_name": result.get("tool_name", ""),
            "server_id": result.get("server_id", ""),
            "output": result.get("output", {}),
            "output_hash": result.get("output_hash", ""),
            "status": result.get("status", "DENIED"),
        }
        if "stderr" in result:
            normalized["stderr"] = result["stderr"]
        return normalized

    def list_registered_tools(self) -> list[str]:
        return sorted(self._descriptors.keys())
