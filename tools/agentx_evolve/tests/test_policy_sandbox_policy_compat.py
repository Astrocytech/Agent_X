from pathlib import Path
from agentx_evolve.policy.sandbox_policy_compat import SandboxPolicyCompat, SANDBOX_POLICY_INTEGRATION_FAILED


class TestSandboxPolicyCompat:
    def test_constants(self):
        assert SANDBOX_POLICY_INTEGRATION_FAILED == "SANDBOX_POLICY_INTEGRATION_FAILED"

    def test_is_available_default(self):
        compat = SandboxPolicyCompat()
        assert compat.is_available() is True

    def test_request_sandbox_check_with_path_string(self):
        compat = SandboxPolicyCompat()
        result = compat.request_sandbox_check("/tmp/test", "WRITE")
        assert result["success"] is True
        assert result["sandbox_required"] is True
        assert result["path"] == "/tmp/test"
        assert result["operation"] == "WRITE"

    def test_request_sandbox_check_with_path_object(self):
        compat = SandboxPolicyCompat()
        result = compat.request_sandbox_check(Path("/some/path"), "READ")
        assert result["path"] == "/some/path"

    def test_request_sandbox_check_with_metadata(self):
        compat = SandboxPolicyCompat()
        result = compat.request_sandbox_check("/p", "EXECUTE", {"user": "test"})
        assert result["success"] is True
