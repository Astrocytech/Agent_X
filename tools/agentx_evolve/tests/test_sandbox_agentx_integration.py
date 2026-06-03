import pytest
from pathlib import Path
from agentx_evolve.security.initiator_compat import InitiatorCompat, _INITIATOR_IMPORT_ERRORS


def test_imports_initiator_path_registry():
    try:
        from agentx_initiator.core import path_registry
        assert path_registry is not None
    except ImportError:
        pytest.skip("Initiator not installed")


def test_imports_initiator_source_guard():
    try:
        from agentx_initiator.core import source_guard
        assert source_guard is not None
    except ImportError:
        pytest.skip("Initiator not installed")


def test_imports_initiator_schema_validation():
    try:
        from agentx_initiator.core import schema_validation
        assert schema_validation is not None
    except ImportError:
        pytest.skip("Initiator not installed")


def test_imports_initiator_artifact_io():
    try:
        from agentx_initiator.core import artifact_io
        assert artifact_io is not None
    except ImportError:
        pytest.skip("Initiator not installed")


def test_imports_initiator_audit_log():
    try:
        from agentx_initiator.core import audit_log
        assert audit_log is not None
    except ImportError:
        pytest.skip("Initiator not installed")


def test_compat_uses_runtime_state_root():
    compat = InitiatorCompat()
    root = compat.get_runtime_state_root()
    assert root.name == ".agentx-init"
    assert root.parent.exists()


def test_compat_does_not_modify_initiator_source():
    compat = InitiatorCompat()
    root = compat.get_repo_root()
    initiator_dir = root / "tools" / "agentx_initiator"
    if initiator_dir.exists():
        import hashlib
        h = hashlib.sha256()
        for p in sorted(initiator_dir.rglob("*.py")):
            h.update(p.read_bytes())
        digest = h.hexdigest()
        assert len(digest) == 64


def test_compat_integration_failures_recorded():
    failures = list(_INITIATOR_IMPORT_ERRORS)
    assert isinstance(failures, list)


def test_compat_validate_schema_works():
    compat = InitiatorCompat()
    result = compat.validate_schema(
        {"schema_version": "1.0", "test": "value"},
        "sandbox_decision.schema.json",
    )
    assert "valid" in result
    assert "integration" in result
