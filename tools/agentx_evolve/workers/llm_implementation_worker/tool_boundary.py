from __future__ import annotations

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    LLMWorkerResult,
    utc_now_iso,
    new_id,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    WORKER_BLOCKED,
    DEP_MISSING,
    SOURCE_COMPONENT,
)
from agentx_evolve.workers.llm_implementation_worker.worker_errors import (
    WORKER_TOOL_REQUEST_DENIED,
    WORKER_DIRECT_MUTATION_BLOCKED,
)


DIRECT_MUTATION_BYPASS_REASONS = [
    "direct source write",
    "direct shell execution",
    "direct subprocess execution",
    "direct Git write",
    "direct patch application",
    "direct network call",
    "direct MCP server call",
]


def build_tool_request(
    task: LLMWorkerTask,
    tool_name: str,
    arguments: dict,
    requested_effect: str,
) -> dict:
    return {
        "tool_request_id": new_id("tr"),
        "task_id": task.task_id,
        "tool_name": tool_name,
        "arguments": arguments,
        "requested_effect": requested_effect,
        "source_component": SOURCE_COMPONENT,
        "worker_mode": task.worker_mode,
        "timestamp": utc_now_iso(),
    }


def request_tool_via_adapter(
    tool_request: dict,
    tool_context: dict,
) -> dict:
    adapter_status = tool_context.get("status", DEP_MISSING)

    if adapter_status == DEP_MISSING:
        return {
            "tool_request_id": tool_request.get("tool_request_id", ""),
            "status": "BLOCKED",
            "reason": "Tool adapter is missing. Tool request blocked.",
            "failure_class": WORKER_TOOL_REQUEST_DENIED,
            "errors": ["Tool adapter unavailable"],
            "result": None,
        }

    try:
        adapter_fn = tool_context.get("adapter_fn")
        if adapter_fn is None:
            return {
                "tool_request_id": tool_request.get("tool_request_id", ""),
                "status": "FAILED",
                "reason": "No adapter function provided.",
                "failure_class": WORKER_TOOL_REQUEST_DENIED,
                "errors": ["No adapter function"],
                "result": None,
            }

        result = adapter_fn(tool_request=tool_request)
        return result

    except Exception as e:
        return {
            "tool_request_id": tool_request.get("tool_request_id", ""),
            "status": "FAILED",
            "reason": f"Tool adapter call failed: {e}",
            "failure_class": WORKER_TOOL_REQUEST_DENIED,
            "errors": [f"Adapter exception: {e}"],
            "result": None,
        }


def block_direct_tool_bypass(reason: str) -> LLMWorkerResult:
    return LLMWorkerResult(
        worker_result_id=new_id("wr"),
        created_at=utc_now_iso(),
        task_id="",
        status=WORKER_BLOCKED,
        message=f"Direct tool bypass blocked: {reason}",
        failure_class=WORKER_DIRECT_MUTATION_BLOCKED,
        errors=[f"Attempted: {reason}"],
    )
