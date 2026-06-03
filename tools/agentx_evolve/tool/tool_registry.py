from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
from agentx_evolve.tool.tool_models import (
    ToolDefinition, ToolCall, ToolResult, ToolParameter,
    TS_SUCCESS, TS_FAILED, TS_INVALID,
    new_id, utc_now_iso, to_dict,
)
from agentx_evolve.tool.tool_policy import ToolPolicyEnforcer, ToolPolicyResult

ToolHandler = Callable[[ToolCall], ToolResult]


@dataclass
class ToolAuditEntry:
    call_id: str = ""
    timestamp: str = ""
    tool_name: str = ""
    status: str = ""
    duration_ms: float = 0.0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return to_dict(self)


class ToolRegistry:
    def __init__(self, policy: ToolPolicyEnforcer | None = None):
        self._definitions: dict[str, ToolDefinition] = {}
        self._handlers: dict[str, ToolHandler] = {}
        self._audit_log: list[ToolAuditEntry] = []
        self._policy = policy or ToolPolicyEnforcer()

    def register(
        self,
        defn: ToolDefinition,
        handler: ToolHandler,
    ) -> ToolDefinition:
        self._definitions[defn.tool_name] = defn
        self._handlers[defn.tool_name] = handler
        return defn

    def get_definition(self, tool_name: str) -> ToolDefinition | None:
        return self._definitions.get(tool_name)

    def get_handler(self, tool_name: str) -> ToolHandler | None:
        return self._handlers.get(tool_name)

    def has_tool(self, tool_name: str) -> bool:
        return tool_name in self._definitions

    def list_tools(self) -> list[ToolDefinition]:
        return [d for d in self._definitions.values() if d.enabled]

    def list_all(self) -> list[ToolDefinition]:
        return list(self._definitions.values())

    def remove(self, tool_name: str) -> bool:
        self._definitions.pop(tool_name, None)
        self._handlers.pop(tool_name, None)
        return True

    def call_tool(self, tool_name: str, arguments: dict[str, Any], session_id: str = "") -> ToolResult:
        call = ToolCall(
            call_id=new_id("tc"),
            timestamp=utc_now_iso(),
            tool_name=tool_name,
            arguments=arguments,
            session_id=session_id,
        )
        return self.execute_call(call)

    def execute_call(self, call: ToolCall) -> ToolResult:
        defn = self._definitions.get(call.tool_name)
        if defn is None:
            return ToolResult(
                result_id=new_id("tr"),
                timestamp=utc_now_iso(),
                tool_name=call.tool_name,
                status=TS_FAILED,
                message=f"Unknown tool: '{call.tool_name}'",
                errors=[f"Tool '{call.tool_name}' is not registered"],
            )
        if not defn.enabled:
            return ToolResult(
                result_id=new_id("tr"),
                timestamp=utc_now_iso(),
                tool_name=call.tool_name,
                status=TS_FAILED,
                message=f"Tool '{call.tool_name}' is disabled",
                errors=[f"Tool '{call.tool_name}' is disabled"],
            )
        policy_check = self._policy.check_tool_call(call, defn)
        if policy_check.status != TS_SUCCESS:
            return policy_check

        handler = self._handlers.get(call.tool_name)
        if handler is None:
            return ToolResult(
                result_id=new_id("tr"),
                timestamp=utc_now_iso(),
                tool_name=call.tool_name,
                status=TS_FAILED,
                message=f"No handler for tool: '{call.tool_name}'",
                errors=[f"No handler registered for '{call.tool_name}'"],
            )

        import time
        start = time.monotonic()
        try:
            result = handler(call)
        except Exception as e:
            duration = (time.monotonic() - start) * 1000
            self._audit(call, TS_FAILED, duration, errors=[str(e)])
            return ToolResult(
                result_id=new_id("tr"),
                timestamp=utc_now_iso(),
                tool_name=call.tool_name,
                status=TS_FAILED,
                message=f"Handler raised: {e}",
                errors=[str(e)],
            )
        duration = (time.monotonic() - start) * 1000
        result.tool_name = call.tool_name
        result.warnings = list(set(result.warnings + policy_check.warnings))
        self._audit(call, result.status, duration, result.warnings, result.errors)
        return result

    def _audit(
        self,
        call: ToolCall,
        status: str,
        duration_ms: float,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
    ) -> None:
        self._audit_log.append(ToolAuditEntry(
            call_id=call.call_id,
            timestamp=utc_now_iso(),
            tool_name=call.tool_name,
            status=status,
            duration_ms=round(duration_ms, 2),
            warnings=warnings or [],
            errors=errors or [],
        ))

    def get_audit_log(self) -> list[ToolAuditEntry]:
        return list(self._audit_log)

    def clear_audit_log(self) -> None:
        self._audit_log.clear()

    @property
    def policy(self) -> ToolPolicyEnforcer:
        return self._policy
