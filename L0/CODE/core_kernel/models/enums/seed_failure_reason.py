from __future__ import annotations

from enum import Enum


class SeedFailureReason(str, Enum):
    PLANNER_ERROR = "planner_error"
    GATEWAY_ERROR = "gateway_error"
    POLICY_DENIED = "policy_denied"
    GOVERNANCE_DENIED = "governance_denied"
    APPROVAL_REQUIRED = "approval_required"
    APPROVAL_DENIED = "approval_denied"
    EMPTY_INPUT = "empty_input"
    NO_ACTION = "no_action"
    NO_DECISION = "no_decision"
    TOOL_FAILED = "tool_failed"
    TOOL_BLOCKED = "tool_blocked"
    MEMORY_FAILED = "memory_failed"
    EVALUATION_FAILED = "evaluation_failed"
    TRACE_FAILED = "trace_failed"
    CHECKPOINT_FAILED = "checkpoint_failed"
    NO_OUTPUT = "no_output"
    UNKNOWN = "unknown"
