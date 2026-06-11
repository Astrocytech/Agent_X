from agentx_evolve.simulation.simulation_engine import MvpSimulationEngine


class TestMvpSimulationEngine:
    def setup_method(self):
        self.engine = MvpSimulationEngine()

    def test_simulate_report_generation(self):
        class FakeAction:
            action_id = "act-1"
        result = self.engine.simulate(FakeAction(), {
            "action_type": "report_generation",
            "target_path": "/tmp/report.json",
            "size_estimate": 512,
        })
        assert result.action_id == "act-1"
        assert len(result.predicted_changes) == 1
        assert result.predicted_changes[0]["type"] == "artifact_write"

    def test_rollback_required_without_plan(self):
        class FakeAction:
            action_id = "act-2"
        result = self.engine.simulate(FakeAction(), {
            "requires_rollback": True,
            "rollback_plan_id": None,
        })
        assert not result.safe_to_execute
        assert "Rollback plan" in result.reason

    def test_rollback_required_with_plan(self):
        class FakeAction:
            action_id = "act-3"
        result = self.engine.simulate(FakeAction(), {
            "requires_rollback": True,
            "rollback_plan_id": "rb-1",
        })
        assert result.safe_to_execute

    def test_latest_result(self):
        class FakeAction:
            action_id = "act-4"
        self.engine.simulate(FakeAction(), {})
        assert self.engine.latest() is not None

    def test_clear(self):
        class FakeAction:
            action_id = "act-5"
        self.engine.simulate(FakeAction(), {})
        self.engine.clear()
        assert self.engine.latest() is None
