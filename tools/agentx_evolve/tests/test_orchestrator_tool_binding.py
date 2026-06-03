import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.tool_binding import invoke_tool_for_step
from agentx_evolve.orchestrator.orchestrator_models import ExecutionStep


def _make_step(step_id="s-1", run_id="r-1", step_name="read_file", assigned_role="tool_agent"):
    return ExecutionStep(step_id=step_id, run_id=run_id, step_name=step_name, assigned_role=assigned_role)


def test_invoke_tool_for_step_success():
    step = _make_step()

    def adapter_fn(**kwargs):
        return {"status": "OK", "output": "file content"}

    binding, result = invoke_tool_for_step(step, "source_reader", {"effect": "read", "path": "test.py"}, adapter_fn, {})
    assert binding.dispatch_status == "COMPLETED"
    assert result["status"] == "OK"


def test_invoke_tool_for_step_blocked_tool():
    step = _make_step()
    binding, result = invoke_tool_for_step(step, "unknown_tool", {}, None, {})
    assert binding.dispatch_status == "BLOCKED"
    assert "not allowed" in binding.errors[-1]


def test_invoke_tool_for_step_no_adapter():
    step = _make_step()
    binding, result = invoke_tool_for_step(step, "source_reader", {}, None, {})
    assert binding.dispatch_status == "BLOCKED"
    assert "unavailable" in binding.errors[-1]


def test_invoke_tool_for_step_adapter_exception():
    step = _make_step()

    def adapter_fn(**kwargs):
        raise RuntimeError("Adapter crashed")

    binding, result = invoke_tool_for_step(step, "source_reader", {}, adapter_fn, {})
    assert binding.dispatch_status == "FAILED"
    assert "Adapter crashed" in binding.errors[-1]


def test_invoke_tool_for_step_wrong_role():
    step = _make_step(assigned_role="orchestrator")
    binding, result = invoke_tool_for_step(step, "source_reader", {}, None, {})
    assert binding.dispatch_status == "BLOCKED"
    assert "not allowed" in binding.errors[-1]


def test_invoke_tool_for_step_sets_idempotency():
    step = _make_step(step_id="s-tool-1")

    def adapter_fn(**kwargs):
        return {"status": "OK"}

    binding, _ = invoke_tool_for_step(step, "source_reader", {}, adapter_fn, {})
    assert "s-tool-1" in binding.idempotency_key
    assert "source_reader" in binding.idempotency_key


def test_invoke_tool_for_step_captures_arguments():
    step = _make_step()

    def adapter_fn(**kwargs):
        return {"status": "OK"}

    binding, _ = invoke_tool_for_step(step, "source_reader", {"effect": "write", "path": "test.py"}, adapter_fn, {})
    assert binding.requested_effect == "write"
    assert "test.py" in binding.arguments_summary
