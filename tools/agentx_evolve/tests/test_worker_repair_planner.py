import pytest
from agentx_evolve.worker.repair_planner import plan_repair


class TestPlanRepair:
    def test_plan_default(self):
        result = plan_repair({"failure_type": "COMPILE_ERROR", "message": "syntax error"})
        assert result["failure_type"] == "COMPILE_ERROR"
        assert result["description"] == "syntax error"
        assert result["status"] == "planned"

    def test_plan_unknown_failure(self):
        result = plan_repair({})
        assert result["failure_type"] == "UNKNOWN"
