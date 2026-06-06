import tempfile
from pathlib import Path
from agentx_evolve.security.security_models import (
    DECISION_ALLOW, DECISION_BLOCK, DECISION_WARN,
    DECISION_NEEDS_GOVERNANCE, DECISION_NEEDS_ROLLBACK_SNAPSHOT,
    DECISION_NEEDS_SESSION,
    STATUS_SUCCESS, STATUS_BLOCKED, STATUS_FAILED, STATUS_DRY_RUN, STATUS_PASS,
    OP_READ, OP_WRITE, OP_EDIT, OP_PATCH_PRECHECK, OP_SUBPROCESS, OP_NETWORK, OP_REDACT,
    utc_now_iso, new_id, to_dict, sha256_text, sha256_file, has_control_chars,
    SandboxPolicy, SandboxDecision, SandboxViolation,
    PathBoundaryResult, SafeFileOperationResult, SafeSubprocessResult,
    NetworkPolicyResult, SecretRedactionResult,
)


class TestConstants:
    def test_decisions(self):
        assert DECISION_ALLOW == "ALLOW"
        assert DECISION_BLOCK == "BLOCK"
        assert DECISION_WARN == "WARN"
        assert DECISION_NEEDS_GOVERNANCE == "NEEDS_GOVERNANCE"

    def test_statuses(self):
        assert STATUS_SUCCESS == "SUCCESS"
        assert STATUS_BLOCKED == "BLOCKED"
        assert STATUS_FAILED == "FAILED"
        assert STATUS_DRY_RUN == "DRY_RUN"
        assert STATUS_PASS == "PASS"

    def test_operations(self):
        assert OP_READ == "READ"
        assert OP_WRITE == "WRITE"
        assert OP_EDIT == "EDIT"
        assert OP_SUBPROCESS == "SUBPROCESS"
        assert OP_NETWORK == "NETWORK"
        assert OP_REDACT == "REDACT"


class TestHelpers:
    def test_utc_now_iso(self):
        now = utc_now_iso()
        assert "T" in now

    def test_new_id_with_prefix(self):
        val = new_id("test")
        assert val.startswith("test-")
        assert len(val) > 10

    def test_new_id_without_prefix(self):
        val = new_id()
        assert "-" not in val

    def test_to_dict_dataclass(self):
        obj = SandboxPolicy(policy_id="p1")
        d = to_dict(obj)
        assert d["policy_id"] == "p1"

    def test_sha256_text(self):
        h = sha256_text("hello")
        assert isinstance(h, str)
        assert len(h) == 64

    def test_sha256_text_deterministic(self):
        assert sha256_text("abc") == sha256_text("abc")

    def test_sha256_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"hello")
            path = f.name
        try:
            h = sha256_file(Path(path))
            assert isinstance(h, str)
            assert len(h) == 64
        finally:
            Path(path).unlink()

    def test_has_control_chars(self):
        assert has_control_chars("normal") is False
        assert has_control_chars("line\nbreak") is False
        assert has_control_chars("bad\x00char") is True
        assert has_control_chars("") is False


class TestSandboxPolicy:
    def test_defaults(self):
        p = SandboxPolicy()
        assert p.schema_version == "1.0"
        assert p.source_write_allowed is False
        assert p.max_file_size_bytes == 1048576

    def test_to_dict(self):
        p = SandboxPolicy(policy_id="p1")
        d = p.to_dict()
        assert d["policy_id"] == "p1"


class TestSandboxDecision:
    def test_defaults(self):
        d = SandboxDecision()
        assert d.decision == DECISION_BLOCK
        assert d.source_component == "SecuritySandbox"

    def test_with_values(self):
        d = SandboxDecision(
            decision_id="dec-1", operation=OP_READ,
            decision=DECISION_ALLOW, reason="allowed",
        )
        assert d.decision == DECISION_ALLOW
        assert d.reason == "allowed"


class TestSandboxViolation:
    def test_defaults(self):
        v = SandboxViolation()
        assert v.violation_type == ""
        assert v.severity == ""

    def test_with_values(self):
        v = SandboxViolation(
            violation_id="v-1", violation_type="path_escape",
            severity="HIGH", reason="escape detected",
        )
        assert v.violation_type == "path_escape"
        assert v.severity == "HIGH"


class TestPathBoundaryResult:
    def test_defaults(self):
        r = PathBoundaryResult()
        assert r.inside_repo is False
        assert r.symlink_escape is False

    def test_to_dict_removes_resolved_path(self):
        r = PathBoundaryResult(input_path="/tmp/test")
        d = r.to_dict()
        assert "resolved_path" not in d


class TestSafeFileOperationResult:
    def test_defaults(self):
        r = SafeFileOperationResult()
        assert r.bytes_read == 0
        assert r.bytes_written == 0

    def test_with_values(self):
        r = SafeFileOperationResult(
            operation_id="op-1", operation=OP_WRITE,
            target_path="/tmp/f", status=STATUS_SUCCESS,
        )
        assert r.status == STATUS_SUCCESS


class TestSafeSubprocessResult:
    def test_defaults(self):
        r = SafeSubprocessResult()
        assert r.command == []
        assert r.timeout_seconds == 0

    def test_to_dict_converts_command(self):
        r = SafeSubprocessResult(command=["ls", "-la"])
        d = r.to_dict()
        assert d["command"] == ["ls", "-la"]


class TestNetworkPolicyResult:
    def test_defaults(self):
        r = NetworkPolicyResult()
        assert r.target is None
        assert r.status == ""


class TestSecretRedactionResult:
    def test_defaults(self):
        r = SecretRedactionResult()
        assert r.redaction_count == 0
        assert r.redacted_text == ""

    def test_with_values(self):
        r = SecretRedactionResult(
            result_id="sr-1", status=STATUS_SUCCESS,
            redacted_text="***", redaction_count=3,
            redaction_types=["API_KEY"],
        )
        assert r.redaction_count == 3
