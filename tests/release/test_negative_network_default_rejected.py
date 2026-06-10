import json, os, sys, tempfile
from pathlib import Path


class TestNegativeNetworkDefaultRejected:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        sys.path.insert(0, str(self.REPO_ROOT / "tools"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        if str(self.REPO_ROOT / "tools") in sys.path:
            sys.path.remove(str(self.REPO_ROOT / "tools"))

    def test_network_disabled_by_default(self):
        from agentx_evolve.security.network_policy import check_network_allowed
        from agentx_evolve.security.security_models import SandboxPolicy, STATUS_BLOCKED

        policy = SandboxPolicy()
        result = check_network_allowed("https://example.com", policy)
        assert result.status == STATUS_BLOCKED
        assert "disabled" in result.reason.lower()

    def test_network_without_target_rejected(self):
        from agentx_evolve.security.network_policy import check_network_allowed
        from agentx_evolve.security.security_models import SandboxPolicy, STATUS_FAILED

        policy = SandboxPolicy(network_allowed=True)
        result = check_network_allowed(None, policy)
        assert result.status == STATUS_FAILED

    def test_network_access_leads_to_blocker(self):
        from agentx_evolve.final_acceptance.final_verdict import calculate_final_verdict
        from agentx_evolve.final_acceptance.acceptance_models import VERDICT_NOT_ACCEPTED

        verdict, rating, blockers, high, followups = calculate_final_verdict(
            blockers=["Network access required but disabled by policy"],
        )
        assert verdict == VERDICT_NOT_ACCEPTED
        assert any("Network" in b for b in blockers)
