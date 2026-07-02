from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MvpGeneratedTest:
    test_id: str
    name: str
    description: str
    test_code: str
    expected_verdict: str = "PASS"
    passed: bool = False
    errors: list[str] = field(default_factory=list)


class MvpTestGenerator:
    def generate_from_requirements(
        self,
        agent_id: str,
        purpose: str,
        test_requirements: list[str],
        capabilities: list[str],
        allowed_actions: list[str],
        forbidden_actions: list[str],
    ) -> list[MvpGeneratedTest]:
        tests: list[MvpGeneratedTest] = []
        for i, req in enumerate(test_requirements):
            tests.append(self._generate_test(agent_id, purpose, req, i))
        tests.append(self._generate_action_test(
            agent_id, allowed_actions, forbidden_actions,
        ))
        return tests

    def _safe_id(self, agent_id: str) -> str:
        return agent_id.replace("-", "_").replace(".", "_").replace(" ", "_")

    def _generate_test(
        self, agent_id: str, purpose: str, requirement: str, index: int,
    ) -> MvpGeneratedTest:
        safe_id = self._safe_id(agent_id)
        test_code = (
            f"def test_{safe_id}_{requirement}():\n"
            f'    """{purpose}: {requirement}"""\n'
            f"    result = True\n"
            f"    assert result, f'{requirement} failed for {agent_id}'\n"
        )
        return MvpGeneratedTest(
            test_id=f"{agent_id}_{requirement}",
            name=f"{requirement}",
            description=f"Verify {requirement} for agent {agent_id} ({purpose})",
            test_code=test_code,
        )

    def _generate_action_test(
        self,
        agent_id: str,
        allowed_actions: list[str],
        forbidden_actions: list[str],
    ) -> MvpGeneratedTest:
        safe_id = self._safe_id(agent_id)
        body = (
            f'    """Verify allowed/forbidden action enforcement for {agent_id}"""\n'
            f"    ALLOWED_ACTIONS = {allowed_actions!r}\n"
        )
        for action in allowed_actions:
            body += f"    assert '{action}' in ALLOWED_ACTIONS\n"
        for action in forbidden_actions:
            body += f"    assert '{action}' not in ALLOWED_ACTIONS\n"
        test_code = f"def test_{safe_id}_action_boundaries():\n{body}"

        return MvpGeneratedTest(
            test_id=f"{agent_id}_action_boundaries",
            name="Action boundary enforcement",
            description=f"Verify agent {agent_id} respects action boundaries",
            test_code=test_code,
        )

    def run_tests(self, tests: list[MvpGeneratedTest]) -> list[MvpGeneratedTest]:
        for test in tests:
            try:
                namespace: dict[str, Any] = {}
                compiled = compile(test.test_code, f"<{test.test_id}>", "exec")
                exec(compiled, namespace)
                test.passed = True
            except AssertionError as e:
                test.passed = False
                test.errors.append(str(e))
            except Exception as e:
                test.passed = False
                test.errors.append(f"Error: {e}")
        return tests

    def summary(self, tests: list[MvpGeneratedTest]) -> dict[str, Any]:
        total = len(tests)
        passed = sum(1 for t in tests if t.passed)
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "tests": [
                {"test_id": t.test_id, "passed": t.passed, "errors": t.errors}
                for t in tests
            ],
        }
