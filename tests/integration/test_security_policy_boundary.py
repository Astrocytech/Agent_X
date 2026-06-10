import json, os, sys, tempfile
from pathlib import Path
from agentx_evolve.security.path_boundary import check_path_boundary, normalize_repo_path
from agentx_evolve.security.network_policy import check_network_allowed
from agentx_evolve.security.safe_subprocess import check_subprocess_allowed
from agentx_evolve.security.secret_redactor import redact_secrets
from agentx_evolve.security.sandbox_policy import default_sandbox_policy


class TestSecurityPolicyBoundary:
    def setup_method(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.repo_root = self.tmpdir / "repo"
        self.repo_root.mkdir()
        self.policy = default_sandbox_policy(self.repo_root)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_path_traversal_is_blocked(self):
        result = normalize_repo_path(
            "/etc/passwd", self.repo_root, self.policy, operation="READ"
        )
        assert result.status == "BLOCKED"
        assert not result.inside_repo

    def test_l0_writes_are_blocked(self):
        (self.repo_root / "L0").mkdir(exist_ok=True)
        decision = check_path_boundary(
            "L0/test.py", self.repo_root, "WRITE", self.policy
        )
        assert decision.decision == "BLOCK"
        assert "L0" in decision.reason

    def test_network_is_denied_by_default(self):
        result = check_network_allowed("https://example.com", self.policy)
        assert result.status == "BLOCKED"
        assert "disabled" in result.reason.lower()

    def test_unknown_commands_are_blocked(self):
        result = check_subprocess_allowed(["curl", "http://evil.com"], self.policy)
        assert result.status == "BLOCK" or result.status == "BLOCKED"

    def test_secret_values_are_redacted(self):
        result = redact_secrets(
            "export OPENAI_API_KEY = sk-abc123def456ghi789jkl", self.policy
        )
        assert result.redaction_count > 0
        assert "REDACTED" in result.redacted_text
