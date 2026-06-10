import json, os, sys, tempfile
from pathlib import Path
from agentx_evolve.security.path_boundary import check_path_boundary
from agentx_evolve.security.network_policy import check_network_allowed
from agentx_evolve.security.safe_subprocess import check_subprocess_allowed
from agentx_evolve.security.sandbox_policy import default_sandbox_policy
from agentx_evolve.policy.policy_enforcer import PolicyEnforcer
from agentx_evolve.policy.capability_registry import CapabilityRegistryImpl


class TestPolicyBypassResistance:
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.repo_root = self.tmpdir / "repo"
        self.repo_root.mkdir()
        self.policy = default_sandbox_policy(self.repo_root)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_path_boundary_cannot_be_bypassed_via_direct_resolve_call(self):
        from agentx_evolve.security.path_boundary import normalize_repo_path
        outside_path = "/etc/shadow"
        result = normalize_repo_path(outside_path, self.repo_root, self.policy, "READ")
        assert result.status == "BLOCKED"
        assert not result.inside_repo

    def test_network_check_blocks_by_default(self):
        result = check_network_allowed("http://evil.com", self.policy)
        assert result.status == "BLOCKED"

    def test_subprocess_blocks_unknown_commands(self):
        result = check_subprocess_allowed(["custom_tool", "--dangerous"], self.policy)
        assert result.status == "BLOCK" or result.status == "BLOCKED"

    def test_unknown_capabilities_fail_closed(self):
        registry = CapabilityRegistryImpl()
        enforcer = PolicyEnforcer(registry)
        result = enforcer.enforce("unknown_tool", "READ")
        assert result.decision == "BLOCK"
        assert "not registered" in result.reason.lower()
