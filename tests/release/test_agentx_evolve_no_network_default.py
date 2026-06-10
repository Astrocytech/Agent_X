import json, os, sys, tempfile
from pathlib import Path


class TestAgentxEvolveNoNetworkDefault:
    """Test that network policy defaults to blocked."""

    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_network_defaults_to_blocked(self):
        from agentx_evolve.security.sandbox_policy import default_sandbox_policy
        from agentx_evolve.security.network_policy import check_network_allowed
        from agentx_evolve.security.security_models import STATUS_BLOCKED

        policy = default_sandbox_policy(self.tmpdir)
        assert not policy.network_allowed

        result = check_network_allowed("https://example.com", policy)
        assert result.status == STATUS_BLOCKED
        assert "disabled" in result.reason.lower()

    def test_network_policy_respects_enable_flag(self):
        from agentx_evolve.security.sandbox_policy import default_sandbox_policy
        from agentx_evolve.security.security_models import SandboxPolicy
        from agentx_evolve.security.network_policy import check_network_allowed
        from agentx_evolve.security.security_models import STATUS_BLOCKED

        policy = default_sandbox_policy(self.tmpdir)
        policy.network_allowed = True
        result = check_network_allowed("https://example.com", policy)
        assert result.status == STATUS_BLOCKED
        assert "allowlist" in result.reason.lower()

    def test_network_policy_explicitly_requires_opt_in(self):
        from agentx_evolve.security.security_models import SandboxPolicy

        policy = SandboxPolicy(repo_root=str(self.tmpdir))
        assert not policy.network_allowed  # default is False

        policy.network_allowed = True
        assert policy.network_allowed
