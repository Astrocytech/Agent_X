from agentx_evolve.tools.tool_models import (
    ToolCall,
    ToolResult,
    STATUS_SUCCESS,
    STATUS_BLOCKED,
    COMMAND_BLOCKED,
    utc_now_iso,
    new_id,
)


def request_human_review(arguments: dict, context: dict | None = None) -> ToolResult:
    return ToolResult(
        tool_result_id=new_id("tr"),
        tool_call_id="",
        timestamp=utc_now_iso(),
        source_component="HumanTools",
        tool_name="request_human_review",
        status=STATUS_BLOCKED,
        exit_code=1,
        message="Human review must be performed through the Human Review layer",
        data={"arguments": arguments, "context": context or {}},
        failure_class=COMMAND_BLOCKED,
    )


def check_human_review_status(arguments: dict, context: dict | None = None) -> ToolResult:
    return ToolResult(
        tool_result_id=new_id("tr"),
        tool_call_id="",
        timestamp=utc_now_iso(),
        source_component="HumanTools",
        tool_name="check_human_review_status",
        status=STATUS_SUCCESS,
        exit_code=0,
        message="No pending human reviews",
        data={"pending_reviews": [], "total_pending": 0},
    )


__all__ = [
    "request_human_review",
    "check_human_review_status",
]
