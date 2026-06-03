from __future__ import annotations

import json

from agentx_evolve.models.model_models import (
    ModelResponse,
    ModelProfile,
    MODEL_STATUS_SUCCESS,
    MODEL_STATUS_BLOCKED,
)


def validate_model_response(response: ModelResponse, expected_schema: dict | None = None) -> list[str]:
    errors: list[str] = []

    if not response.model_response_id:
        errors.append("Missing model_response_id")

    if not response.model_request_id:
        errors.append("Missing model_request_id")

    if not response.timestamp:
        errors.append("Missing timestamp")

    if response.status not in {MODEL_STATUS_SUCCESS, MODEL_STATUS_BLOCKED, "FAILED", "PARTIAL", "INVALID", "RETRYABLE"}:
        errors.append(f"Unknown status: {response.status}")

    if response.status == MODEL_STATUS_SUCCESS:
        if not response.raw_output and not response.json_output:
            errors.append("Success response missing both raw_output and json_output")

    return errors


def check_output_against_profile(response: ModelResponse, profile: ModelProfile) -> list[str]:
    errors: list[str] = []

    # Model output cannot request source writes
    if profile.write_source:
        if _output_requests_file_write(response):
            errors.append("Model output requested file write, which is blocked")

    # Model output cannot request tool execution
    if profile.runs_tools:
        if _output_requests_tool_call(response):
            errors.append("Model output requested tool execution, which is blocked")

    # Model output cannot request command execution
    if profile.runs_commands:
        if _output_requests_command_execution(response):
            errors.append("Model output requested command execution, which is blocked")

    return errors


def _output_requests_file_write(response: ModelResponse) -> bool:
    raw = (response.raw_output or "").lower()
    markers = ["write_file", "create_file", "edit_file", "patch_file", "source_write"]
    return any(m in raw for m in markers)


def _output_requests_tool_call(response: ModelResponse) -> bool:
    raw = (response.raw_output or "").lower()
    markers = ["call_tool", "execute_tool", "tool_call", "run_tool"]
    return any(m in raw for m in markers)


def _output_requests_command_execution(response: ModelResponse) -> bool:
    raw = (response.raw_output or "").lower()
    markers = ["exec_command", "run_command", "shell_exec", "bash_exec"]
    return any(m in raw for m in markers)
