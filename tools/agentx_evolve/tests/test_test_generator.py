from agentx_evolve.self_evolution.test_generator import (
    MvpTestGenerator,
    MvpGeneratedTest,
)


class TestMvpTestGenerator:
    def setup_method(self):
        self.generator = MvpTestGenerator()

    def test_generates_from_requirements(self):
        tests = self.generator.generate_from_requirements(
            agent_id="agent-monitor",
            purpose="System monitoring agent",
            test_requirements=["unit_tests_pass", "invariants_hold"],
            capabilities=["goal_execution", "tool_usage"],
            allowed_actions=["read_files", "write_files"],
            forbidden_actions=["delete_files", "modify_system"],
        )
        assert len(tests) == 3
        assert any("unit_tests_pass" in t.test_id for t in tests)
        assert any("invariants_hold" in t.test_id for t in tests)
        assert any("action_boundaries" in t.test_id for t in tests)

    def test_generated_test_code_is_valid_python(self):
        tests = self.generator.generate_from_requirements(
            agent_id="agent-x",
            purpose="test",
            test_requirements=["must_pass"],
            capabilities=["execute"],
            allowed_actions=["read"],
            forbidden_actions=["delete"],
        )
        for test in tests:
            compile(test.test_code, f"<{test.test_id}>", "exec")

    def test_run_tests_passes_for_correct_code(self):
        test = MvpGeneratedTest(
            test_id="test_ok",
            name="should pass",
            description="this should pass",
            test_code="result = 1 + 1\nassert result == 2",
        )
        results = self.generator.run_tests([test])
        assert results[0].passed is True
        assert results[0].errors == []

    def test_run_tests_captures_assertion_error(self):
        test = MvpGeneratedTest(
            test_id="test_fail",
            name="should fail",
            description="this should fail",
            test_code="assert False, 'intentional failure'",
        )
        results = self.generator.run_tests([test])
        assert results[0].passed is False
        assert len(results[0].errors) > 0

    def test_run_tests_captures_exception(self):
        test = MvpGeneratedTest(
            test_id="test_error",
            name="should error",
            description="this should error",
            test_code="raise ValueError('bad data')",
        )
        results = self.generator.run_tests([test])
        assert results[0].passed is False
        assert any("bad data" in e for e in results[0].errors)

    def test_summary_counts(self):
        tests = [
            MvpGeneratedTest(test_id="p1", name="p", description="",
                             test_code="assert True", passed=True),
            MvpGeneratedTest(test_id="p2", name="p", description="",
                             test_code="assert True", passed=True),
            MvpGeneratedTest(test_id="f1", name="f", description="",
                             test_code="assert False", passed=False),
        ]
        s = self.generator.summary(tests)
        assert s["total"] == 3
        assert s["passed"] == 2
        assert s["failed"] == 1
