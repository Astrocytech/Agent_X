from agentx_evolve.policy.policy_request import PolicyRequest


class TestPolicyRequest:
    def test_defaults(self):
        req = PolicyRequest()
        assert req.request_id == ""
        assert req.caller_role == ""
        assert req.tool_name == ""
        assert req.requested_effect == ""
        assert req.target is None
        assert req.metadata == {}

    def test_with_values(self):
        req = PolicyRequest(
            request_id="req-1",
            caller_role="ORCHESTRATOR",
            tool_name="safe_write",
            requested_effect="WRITE",
            target="src/main.py",
            metadata={"key": "val"},
        )
        assert req.request_id == "req-1"
        assert req.caller_role == "ORCHESTRATOR"
        assert req.tool_name == "safe_write"
        assert req.requested_effect == "WRITE"
        assert req.target == "src/main.py"
        assert req.metadata == {"key": "val"}

    def test_target_none(self):
        req = PolicyRequest(target=None)
        assert req.target is None

    def test_metadata_mutable(self):
        req = PolicyRequest()
        req.metadata["new_key"] = "new_val"
        assert req.metadata["new_key"] == "new_val"
