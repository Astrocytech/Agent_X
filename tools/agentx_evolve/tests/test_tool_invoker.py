import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.orchestrator.tool_invoker import invoke_tool_for_step
from agentx_evolve.orchestrator.orchestrator_models import ExecutionStep
from agentx_evolve.orchestrator.orchestrator_config import STEP_STATUS_PENDING


def _make_step(**overrides) -> ExecutionStep:
    params = dict(
        step_id="s-1",
        plan_id="p-1",
        run_id="run-1",
        step_index=0,
        step_name="execute_source_reader",
        step_type="TOOL",
        assigned_role="tool_agent",
        status=STEP_STATUS_PENDING,
    )
    params.update(overrides)
    return ExecutionStep(**params)


class TestInvokeToolUsesAdapter:
    def test_invoke_tool_uses_adapter(self):
        step = _make_step()
        called = False

        def fake_adapter(**kw):
            nonlocal called
            called = True
            return {"status": "SUCCESS", "results": []}

        binding, result = invoke_tool_for_step(step, "source_reader", {}, fake_adapter, {})
        assert called
        assert result["status"] == "SUCCESS"
        assert binding.dispatch_status == "COMPLETED"


class TestInvokeToolRejectsNotAllowedTool:
    def test_invoke_tool_rejects_not_allowed_tool(self):
        step = _make_step()
        binding, result = invoke_tool_for_step(step, "malicious_rm", {}, None, {})
        assert result["status"] == "BLOCKED"
        assert "not allowed" in result["error"]
        assert binding.dispatch_status == "BLOCKED"


class TestInvokeToolBlocksWhenAdapterNone:
    def test_invoke_tool_blocks_when_adapter_none(self):
        step = _make_step()
        binding, result = invoke_tool_for_step(step, "source_reader", {}, None, {})
        assert result["status"] == "BLOCKED"
        assert "adapter unavailable" in result["error"].lower()
        assert binding.dispatch_status == "BLOCKED"


class TestInvokeToolBlocksForWrongRole:
    def test_invoke_tool_blocks_for_wrong_role(self):
        step = _make_step(assigned_role="orchestrator")
        binding, result = invoke_tool_for_step(step, "source_reader", {}, None, {})
        assert result["status"] == "BLOCKED"
        assert "not allowed" in result["error"].lower()


class TestInvokeToolRecordsBinding:
    def test_invoke_tool_records_binding(self):
        step = _make_step()

        def fake_adapter(**kw):
            return {"status": "SUCCESS", "results": []}

        binding, result = invoke_tool_for_step(step, "source_reader", {"effect": "read"}, fake_adapter, {})
        assert binding.binding_id.startswith("tb-")
        assert binding.step_id == "s-1"
        assert binding.tool_name == "source_reader"
        assert binding.idempotency_key == "tool-s-1-source_reader"


class TestInvokeToolHandlesAdapterException:
    def test_invoke_tool_handles_adapter_exception(self):
        step = _make_step()

        def broken_adapter(**kw):
            raise RuntimeError("adapter crashed")

        binding, result = invoke_tool_for_step(step, "source_reader", {}, broken_adapter, {})
        assert result["status"] == "FAILED"
        assert "adapter crashed" in result["error"]
        assert binding.dispatch_status == "FAILED"
