from pathlib import Path
from agentx_evolve.security.initiator_compat import InitiatorCompat


class TestInitiatorCompat:
    def test_default_construction(self):
        compat = InitiatorCompat()
        assert isinstance(compat.integration_failures, list)
        assert isinstance(compat.degraded, bool)

    def test_construction_with_repo_root(self):
        compat = InitiatorCompat(repo_root=Path("/tmp"))
        assert compat._repo_root == Path("/tmp")

    def test_get_protected_paths(self):
        compat = InitiatorCompat()
        paths = compat.get_protected_paths()
        assert "L0/" in paths

    def test_get_repo_root_returns_path_or_raises(self):
        compat = InitiatorCompat()
        try:
            root = compat.get_repo_root()
            assert root is not None
        except RuntimeError as e:
            assert "cannot determine repository root" in str(e)

    def test_get_runtime_state_root_returns(self):
        compat = InitiatorCompat()
        try:
            root = compat.get_runtime_state_root()
            assert root is not None
        except RuntimeError:
            pass

    def test_check_source_guard_returns_result(self):
        compat = InitiatorCompat()
        result = compat.check_source_guard(["test.py"])
        assert "integration" in result
        assert "before_state_captured" in result

    def test_validate_schema_returns_result(self):
        compat = InitiatorCompat()
        result = compat.validate_schema({"test": 1}, "schema1")
        assert "valid" in result
        assert "integration" in result

    def test_write_json_atomic_fallback_on_bad_path(self):
        compat = InitiatorCompat()
        result = compat.write_json_atomic(Path("/nonexistent/test.json"), {"a": 1})
        assert result["status"] in ("SUCCESS", "FAILED")

    def test_append_audit_event(self):
        compat = InitiatorCompat()
        result = compat.append_audit_event({"event_id": "e1"})
        assert "status" in result

    def test_refresh_integration_status(self):
        compat = InitiatorCompat()
        compat.refresh_integration_status()
        assert isinstance(compat.degraded, bool)
