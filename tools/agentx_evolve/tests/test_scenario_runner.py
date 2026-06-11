from agentx_evolve.testing.scenario_runner import MvpScenarioRunner, MvpScenario


class TestMvpScenarioRunner:
    def test_run_without_orchestrator_fails(self):
        runner = MvpScenarioRunner()
        scenario = MvpScenario(name="test", goal="do something",
                                profile_id="STRICT", expected_result="PASS")
        result = runner.run_scenario(scenario, {})
        assert not result.passed
        assert result.final_verdict == "NOT_RUN"

    def test_run_with_mock_orchestrator(self):
        def mock_orch(scenario, ctx):
            return {"verdict": "PASS", "errors": [], "evidence_refs": []}

        runner = MvpScenarioRunner(orchestrator_fn=mock_orch)
        scenario = MvpScenario(name="pass_test", goal="pass",
                                profile_id="STRICT", expected_result="PASS")
        result = runner.run_scenario(scenario, {})
        assert result.passed

    def test_all_passed(self):
        def mock_orch(scenario, ctx):
            return {"verdict": scenario.expected_result, "errors": [], "evidence_refs": []}

        runner = MvpScenarioRunner(orchestrator_fn=mock_orch)
        runner.run_scenario(MvpScenario(name="s1", goal="", profile_id="STRICT",
                                         expected_result="PASS"), {})
        runner.run_scenario(MvpScenario(name="s2", goal="", profile_id="STRICT",
                                         expected_result="PASS"), {})
        assert runner.all_passed()
