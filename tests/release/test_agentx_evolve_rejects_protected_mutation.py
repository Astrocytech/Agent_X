import json, os, sys, tempfile
from pathlib import Path


class TestAgentxEvolveRejectsProtectedMutation:
    """Test that protected path mutations (e.g. L0/) are rejected."""

    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_l0_write_is_blocked(self):
        from agentx_evolve.security.path_boundary import check_path_boundary
        from agentx_evolve.security.sandbox_policy import default_sandbox_policy
        from agentx_evolve.security.security_models import DECISION_BLOCK

        policy = default_sandbox_policy(self.tmpdir)
        decision = check_path_boundary("L0/some_file.py", self.tmpdir, "WRITE", policy)
        assert decision.decision == DECISION_BLOCK
        assert "L0" in decision.reason or "blocked" in decision.reason.lower()

    def test_protected_path_write_is_blocked(self):
        from agentx_evolve.security.path_boundary import check_path_boundary
        from agentx_evolve.security.sandbox_policy import default_sandbox_policy
        from agentx_evolve.security.security_models import DECISION_BLOCK

        policy = default_sandbox_policy(self.tmpdir)
        decision = check_path_boundary("L0/", self.tmpdir, "PATCH_PRECHECK", policy)
        assert decision.decision == DECISION_BLOCK

    def test_source_write_disabled_by_default(self):
        from agentx_evolve.security.path_boundary import check_path_boundary
        from agentx_evolve.security.sandbox_policy import default_sandbox_policy
        from agentx_evolve.security.security_models import DECISION_BLOCK

        policy = default_sandbox_policy(self.tmpdir)
        decision = check_path_boundary("tools/some_file.py", self.tmpdir, "WRITE", policy)
        assert decision.decision == DECISION_BLOCK
        assert "disabled" in decision.reason.lower()

    def test_runtime_write_allowed(self):
        from agentx_evolve.security.path_boundary import check_path_boundary
        from agentx_evolve.security.sandbox_policy import default_sandbox_policy
        from agentx_evolve.security.security_models import DECISION_ALLOW

        policy = default_sandbox_policy(self.tmpdir)
        decision = check_path_boundary(".agentx-init/test.txt", self.tmpdir, "WRITE", policy)
        assert decision.decision == DECISION_ALLOW
