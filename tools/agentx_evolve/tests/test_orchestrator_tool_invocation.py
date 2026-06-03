import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.tool_invocation import (
    invoke_tool_for_step,
    ALLOWED_TOOLS,
)
from agentx_evolve.orchestrator.orchestrator_models import ExecutionStep


def test_allowed_tools():
    assert "source_reader" in ALLOWED_TOOLS
    assert "file_lister" in ALLOWED_TOOLS
    assert "diff_viewer" in ALLOWED_TOOLS
    assert "search_code" in ALLOWED_TOOLS
    assert "read_file" in ALLOWED_TOOLS
    assert len(ALLOWED_TOOLS) == 5


def _make_step(step_id="s-1", run_id="r-1", step_name="read_file", assigned_role="tool_agent"):
    return ExecutionStep(step_id=step_id, run_id=run_id, step_name=step_name, assigned_role=assigned_role)


def test_invoke_tool_for_step_success():
    step = _make_step()

    def adapter_fn(**kwargs):
        return {"status": "OK", "output": "file content"}

    binding, result = invoke_tool_for_step(step, "source_reader", {"effect": "read"}, adapter_fn, {})
    assert binding.dispatch_status == "COMPLETED"
    assert result["status"] == "OK"
    assert binding.tool_name == "source_reader"


def test_invoke_tool_for_step_blocked():
    step = _make_step()
    binding, result = invoke_tool_for_step(step, "invalid_tool", {}, None, {})
    assert binding.dispatch_status == "BLOCKED"
    assert "not allowed" in binding.errors[-1]


def test_invoke_tool_for_step_null_adapter():
    step = _make_step()
    binding, result = invoke_tool_for_step(step, "source_reader", {}, None, {})
    assert binding.dispatch_status == "BLOCKED"
    assert "unavailable" in binding.errors[-1]


def test_invoke_tool_for_step_adapter_exception():
    step = _make_step()

    def broken(**kwargs):
        raise ValueError("Tool error")

    binding, result = invoke_tool_for_step(step, "source_reader", {}, broken, {})
    assert binding.dispatch_status == "FAILED"
    assert "Tool error" in binding.errors[-1]


def test_invoke_tool_for_step_role_mismatch():
    step = _make_step(assigned_role="orchestrator")
    binding, result = invoke_tool_for_step(step, "source_reader", {}, None, {})
    assert binding.dispatch_status == "BLOCKED"


def test_invoke_tool_for_step_idempotency():
    step = _make_step(step_id="s-ti-1")

    def adapter_fn(**kwargs):
        return {"status": "OK"}

    binding, _ = invoke_tool_for_step(step, "file_lister", {}, adapter_fn, {})
    assert "s-ti-1" in binding.idempotency_key
    assert "file_lister" in binding.idempotency_key


def test_invoke_tool_for_step_effect_read():
    step = _make_step()

    def adapter_fn(**kwargs):
        return {"status": "OK"}

    binding, _ = invoke_tool_for_step(step, "diff_viewer", {"effect": "read", "path": "a.txt"}, adapter_fn, {})
    assert binding.requested_effect == "read"
