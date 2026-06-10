import json, os, sys, tempfile
from pathlib import Path


class TestAgentxEvolveMockSelfEvolution:
    """Test orchestrator setup with mock provider in a temp workspace."""

    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_create_orchestration_session_with_bounded_goal(self):
        from agentx_evolve.orchestrator.orchestrator_models import (
            OrchestrationSession, new_id, utc_now_iso,
        )
        from agentx_evolve.orchestrator.orchestrator_config import (
            ORCH_STATUS_CREATED, SESSION_STATUS_ACTIVE,
        )

        session = OrchestrationSession(
            session_id=new_id("session"),
            run_id=new_id("run"),
            created_at=utc_now_iso(),
            updated_at=utc_now_iso(),
            requested_task_id=new_id("task"),
            requested_task_summary="Add docstrings to all public functions",
            initiating_role="developer",
            state=ORCH_STATUS_CREATED,
            session_status=SESSION_STATUS_ACTIVE,
        )
        assert session.session_id.startswith("session-")
        assert session.state == ORCH_STATUS_CREATED
        assert session.session_status == SESSION_STATUS_ACTIVE
        assert not session.is_terminal()
        assert "docstrings" in session.requested_task_summary

    def test_mock_provider_returns_deterministic_response(self):
        from agentx_evolve.providers.mock_provider import MockProvider

        provider = MockProvider()
        models = provider.get_models()
        assert any(m["id"] == "mock/deterministic" for m in models)

        response = provider.complete([{"role": "user", "content": "Say READY"}])
        assert response["content"] == "READY — deterministic Agent_X mock provider response."

    def test_mock_provider_structured_plan(self):
        from agentx_evolve.providers.mock_provider import MockProvider

        provider = MockProvider()
        plan = provider.complete_structured([{"role": "user", "content": "Plan something"}])
        assert plan["summary"] == "mock plan for testing"
        assert len(plan["actions"]) == 1
        assert plan["actions"][0]["type"] == "noop"
