from pathlib import Path
from agentx_evolve.patch_execution.patch_models import (
    SOURCE_COMPONENT,
    SPEC_SCHEMA_VERSION,
    SESSION_STATUS_CREATED,
    SESSION_STATUS_BLOCKED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_ROLLED_BACK,
    SESSION_STATUS_ROLLBACK_FAILED,
    SESSION_STATUS_ACCEPTED,
    OP_EXACT_EDIT,
    OP_WRITE_FILE,
    OP_CREATE_FILE,
    OP_DELETE_FILE,
    OP_RENAME_FILE,
    OP_PATCH_TEXT,
    FINAL_PENDING,
    FINAL_ACCEPT,
    FINAL_REJECT,
    FINAL_ROLLBACK,
    PATCH_PENDING,
    PATCH_APPLIED,
    PATCH_BLOCKED,
    PATCH_FAILED,
    PATCH_DRY_RUN,
    TRIGGER_VALIDATION_FAILED,
    TRIGGER_SOURCE_GUARD_FAILED,
    TRIGGER_PATCH_FAILED,
    TRIGGER_USER_REQUEST,
    TRIGGER_UNKNOWN,
    GUARD_PASS,
    GUARD_BLOCKED,
    GUARD_FAILED,
    VALIDATION_PASS,
    VALIDATION_FAILED,
    VALIDATION_BLOCKED,
    VALIDATION_SKIPPED,
    MODE_DRY_RUN,
    MODE_LIVE,
    LIFECYCLE_STATES,
    FAILURE_TYPES,
    DEFAULT_LIMITS,
    PatchOperation,
    PatchApplication,
    PatchResult,
    RollbackSnapshot,
    RollbackRecord,
    ImplementationSession,
    SourceChangeGuardResult,
    ImplementationValidationGateResult,
    PatchExecutionDecision,
    PatchExecutionAuditEvent,
    DryRunResult,
    SourceInventory,
    TemporaryPolicyBridge,
    PatchLimits,
    utc_now_iso,
    new_id,
    sha256_text,
    sha256_file,
    to_dict,
)


class TestConstants:
    def test_source_component(self):
        assert SOURCE_COMPONENT == "GovernedPatchExecution"

    def test_spec_schema_version(self):
        assert SPEC_SCHEMA_VERSION == "1.0"

    def test_session_status_constants(self):
        assert SESSION_STATUS_CREATED == "CREATED"
        assert SESSION_STATUS_BLOCKED == "BLOCKED"
        assert SESSION_STATUS_FAILED == "FAILED"
        assert SESSION_STATUS_ROLLED_BACK == "ROLLED_BACK"
        assert SESSION_STATUS_ROLLBACK_FAILED == "ROLLBACK_FAILED"
        assert SESSION_STATUS_ACCEPTED == "ACCEPTED"

    def test_operation_type_constants(self):
        assert OP_EXACT_EDIT == "EXACT_EDIT"
        assert OP_WRITE_FILE == "WRITE_FILE"
        assert OP_CREATE_FILE == "CREATE_FILE"
        assert OP_DELETE_FILE == "DELETE_FILE"
        assert OP_RENAME_FILE == "RENAME_FILE"
        assert OP_PATCH_TEXT == "PATCH_TEXT"

    def test_final_decision_constants(self):
        assert FINAL_PENDING == "PENDING"
        assert FINAL_ACCEPT == "ACCEPT"
        assert FINAL_REJECT == "REJECT"
        assert FINAL_ROLLBACK == "ROLLBACK"

    def test_patch_status_constants(self):
        assert PATCH_PENDING == "PENDING"
        assert PATCH_APPLIED == "APPLIED"
        assert PATCH_BLOCKED == "BLOCKED"
        assert PATCH_FAILED == "FAILED"
        assert PATCH_DRY_RUN == "DRY_RUN"

    def test_trigger_constants(self):
        assert TRIGGER_VALIDATION_FAILED == "VALIDATION_FAILED"
        assert TRIGGER_SOURCE_GUARD_FAILED == "SOURCE_GUARD_FAILED"
        assert TRIGGER_PATCH_FAILED == "PATCH_FAILED"
        assert TRIGGER_USER_REQUEST == "USER_REQUEST"
        assert TRIGGER_UNKNOWN == "UNKNOWN"

    def test_guard_status_constants(self):
        assert GUARD_PASS == "PASS"
        assert GUARD_BLOCKED == "BLOCKED"
        assert GUARD_FAILED == "FAILED"

    def test_validation_status_constants(self):
        assert VALIDATION_PASS == "PASS"
        assert VALIDATION_FAILED == "FAILED"
        assert VALIDATION_BLOCKED == "BLOCKED"
        assert VALIDATION_SKIPPED == "SKIPPED"

    def test_mode_constants(self):
        assert MODE_DRY_RUN == "DRY_RUN"
        assert MODE_LIVE == "LIVE"

    def test_lifecycle_states(self):
        expected = [
            "CREATED",
            "PROPOSAL_LOADED",
            "GOVERNANCE_CHECKED",
            "POLICY_CHECKED",
            "SANDBOX_CHECKED",
            "DRY_RUN_READY",
            "SNAPSHOT_CREATED",
            "PATCH_APPLIED",
            "SOURCE_GUARD_CHECKED",
            "VALIDATION_RUNNING",
            "VALIDATION_PASSED",
            "VALIDATION_FAILED",
            "ROLLBACK_RUNNING",
            "ROLLED_BACK",
            "ROLLBACK_FAILED",
            "ACCEPTED",
            "FAILED",
            "BLOCKED",
        ]
        assert LIFECYCLE_STATES == expected

    def test_failure_types(self):
        expected = {
            "PATCH_SESSION_CREATE_FAILED",
            "PATCH_PROPOSAL_INVALID",
            "PATCH_POLICY_BLOCKED",
            "PATCH_SANDBOX_BLOCKED",
            "PATCH_TARGET_OUTSIDE_SCOPE",
            "PATCH_TARGET_L0_BLOCKED",
            "PATCH_TARGET_PROTECTED_BLOCKED",
            "PATCH_TARGET_SYMLINK_ESCAPE",
            "PATCH_LIMIT_EXCEEDED",
            "PATCH_BINARY_BLOCKED",
            "PATCH_ENCODING_FAILED",
            "DRY_RUN_FAILED",
            "ROLLBACK_SNAPSHOT_FAILED",
            "PATCH_APPLY_FAILED",
            "PARTIAL_APPLY_FAILED",
            "SOURCE_INVENTORY_FAILED",
            "SOURCE_CHANGE_GUARD_FAILED",
            "VALIDATION_COMMAND_BLOCKED",
            "VALIDATION_FAILED",
            "ROLLBACK_FAILED",
            "EVIDENCE_WRITE_FAILED",
            "SCHEMA_VALIDATION_FAILED",
            "LOCK_CONFLICT",
            "UNKNOWN_PATCH_EXECUTION_ERROR",
        }
        assert FAILURE_TYPES == expected

    def test_default_limits(self):
        expected = {
            "max_changed_files_per_session": 5,
            "max_patch_operations_per_session": 20,
            "max_single_file_bytes": 1048576,
            "max_patch_text_bytes": 262144,
            "max_total_snapshot_bytes": 10485760,
            "max_validation_runtime_seconds": 120,
            "max_session_runtime_seconds": 300,
        }
        assert DEFAULT_LIMITS == expected


class TestHelperFunctions:
    def test_new_id_default_generates_unique(self):
        ids = {new_id() for _ in range(100)}
        assert len(ids) == 100

    def test_new_id_with_prefix(self):
        nid = new_id("sess")
        assert nid.startswith("sess-")
        assert len(nid) > len("sess-")

    def test_new_id_empty_prefix(self):
        nid = new_id("")
        assert "-" not in nid

    def test_utc_now_iso_format(self):
        iso = utc_now_iso()
        assert "T" in iso
        assert iso.endswith("+00:00") or "+00:00" in iso

    def test_sha256_text_known_input(self):
        h = sha256_text("hello")
        expected = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        assert h == expected

    def test_sha256_text_different_inputs_different_hashes(self):
        assert sha256_text("foo") != sha256_text("bar")

    def test_sha256_text_type_and_length(self):
        h = sha256_text("data")
        assert isinstance(h, str)
        assert len(h) == 64

    def test_sha256_file_existing_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        h = sha256_file(f)
        expected = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        assert h == expected

    def test_sha256_file_nonexistent_file(self):
        h = sha256_file(Path("/does/not/exist.txt"))
        assert h is None

    def test_to_dict_converts_dataclass(self):
        op = PatchOperation(operation_id="op-1", operation_type=OP_EXACT_EDIT)
        d = to_dict(op)
        assert isinstance(d, dict)
        assert d["operation_id"] == "op-1"
        assert d["operation_type"] == OP_EXACT_EDIT

    def test_to_dict_converts_path_to_str(self):
        op = PatchOperation(target_path="/some/path")
        d = to_dict(op)
        assert d["target_path"] == "/some/path"

    def test_to_dict_converts_nested_dataclass_list(self):
        app = PatchApplication(application_id="app-1")
        app.operations.append(PatchOperation(operation_id="op-1"))
        d = to_dict(app)
        assert len(d["operations"]) == 1
        assert d["operations"][0]["operation_id"] == "op-1"

    def test_to_dict_returns_dict_unmodified(self):
        d = to_dict({"a": 1})
        assert d == {"a": 1}


class TestPatchOperation:
    def test_default_fields(self):
        op = PatchOperation()
        assert op.operation_id == ""
        assert op.operation_type == OP_EXACT_EDIT
        assert op.target_path == ""
        assert op.old_text is None
        assert op.new_text is None
        assert op.content is None
        assert op.allow_create is False
        assert op.allow_delete is False
        assert op.expected_before_hash is None
        assert op.requires_rollback_snapshot is True
        assert op.approved is False

    def test_custom_values(self):
        op = PatchOperation(
            operation_id="op-1",
            operation_type=OP_WRITE_FILE,
            target_path="/tmp/test.txt",
            old_text="old",
            new_text="new",
            content="content",
            allow_create=True,
            allow_delete=False,
            expected_before_hash="abc",
            requires_rollback_snapshot=False,
            approved=True,
        )
        assert op.operation_id == "op-1"
        assert op.operation_type == OP_WRITE_FILE
        assert op.target_path == "/tmp/test.txt"
        assert op.old_text == "old"
        assert op.new_text == "new"
        assert op.content == "content"
        assert op.allow_create is True
        assert op.allow_delete is False
        assert op.expected_before_hash == "abc"
        assert op.requires_rollback_snapshot is False
        assert op.approved is True


class TestPatchApplication:
    def test_default_fields(self):
        app = PatchApplication()
        assert app.application_id == ""
        assert app.session_id == ""
        assert app.proposal_id is None
        assert app.governance_decision_id is None
        assert app.policy_decision_id is None
        assert app.timestamp == ""
        assert app.source_component == SOURCE_COMPONENT
        assert app.mode == MODE_DRY_RUN
        assert app.operations == []
        assert app.target_paths == []
        assert app.status == PATCH_PENDING
        assert app.before_hashes == {}
        assert app.after_hashes == {}
        assert app.warnings == []
        assert app.errors == []

    def test_custom_values(self):
        ops = [PatchOperation(operation_id="op-1")]
        app = PatchApplication(
            application_id="app-1",
            session_id="sess-1",
            proposal_id="prop-1",
            governance_decision_id="gov-1",
            policy_decision_id="pol-1",
            timestamp="2024-01-01T00:00:00",
            source_component="Custom",
            mode=MODE_LIVE,
            operations=ops,
            target_paths=["/tmp/a.txt"],
            status=PATCH_APPLIED,
            before_hashes={"/tmp/a.txt": "abc"},
            after_hashes={"/tmp/a.txt": "def"},
            warnings=["warn"],
            errors=["err"],
        )
        assert app.application_id == "app-1"
        assert app.mode == MODE_LIVE
        assert len(app.operations) == 1
        assert app.before_hashes["/tmp/a.txt"] == "abc"


class TestPatchResult:
    def test_default_fields(self):
        r = PatchResult()
        assert r.result_id == ""
        assert r.session_id == ""
        assert r.application_id == ""
        assert r.mode == MODE_DRY_RUN
        assert r.status == PATCH_PENDING
        assert r.changed_paths == []
        assert r.created_paths == []
        assert r.deleted_paths == []
        assert r.before_hashes == {}
        assert r.after_hashes == {}
        assert r.warnings == []
        assert r.errors == []

    def test_custom_values(self):
        r = PatchResult(
            result_id="res-1",
            session_id="sess-1",
            application_id="app-1",
            mode=MODE_LIVE,
            status=PATCH_APPLIED,
            changed_paths=["/tmp/a.txt"],
            created_paths=["/tmp/b.txt"],
            deleted_paths=["/tmp/c.txt"],
            before_hashes={"/tmp/a.txt": "abc"},
            after_hashes={"/tmp/a.txt": "def"},
            warnings=["done"],
            errors=[],
        )
        assert r.result_id == "res-1"
        assert r.mode == MODE_LIVE
        assert r.status == PATCH_APPLIED
        assert "/tmp/a.txt" in r.changed_paths


class TestRollbackSnapshot:
    def test_default_fields(self):
        s = RollbackSnapshot()
        assert s.snapshot_id == ""
        assert s.session_id == ""
        assert s.timestamp == ""
        assert s.source_component == "RollbackManager"
        assert s.snapshot_root == ""
        assert s.files == []
        assert s.status == "CREATED"
        assert s.warnings == []
        assert s.errors == []

    def test_custom_values(self):
        s = RollbackSnapshot(
            snapshot_id="snap-1",
            session_id="sess-1",
            timestamp="2024-01-01T00:00:00",
            source_component="CustomGuard",
            snapshot_root="/tmp/snapshots",
            files=[{"path": "/tmp/a.txt", "hash": "abc"}],
            status="COMPLETED",
            warnings=["slow"],
            errors=[],
        )
        assert s.snapshot_id == "snap-1"
        assert s.snapshot_root == "/tmp/snapshots"
        assert s.status == "COMPLETED"
        assert len(s.files) == 1


class TestRollbackRecord:
    def test_default_fields(self):
        r = RollbackRecord()
        assert r.rollback_id == ""
        assert r.session_id == ""
        assert r.snapshot_id == ""
        assert r.timestamp == ""
        assert r.source_component == "RollbackManager"
        assert r.trigger == TRIGGER_UNKNOWN
        assert r.restored_files == []
        assert r.removed_created_files == []
        assert r.verification_status == GUARD_PASS
        assert r.status == SESSION_STATUS_ROLLED_BACK
        assert r.warnings == []
        assert r.errors == []

    def test_custom_values(self):
        r = RollbackRecord(
            rollback_id="rb-1",
            session_id="sess-1",
            snapshot_id="snap-1",
            timestamp="2024-01-01T00:00:00",
            source_component="Custom",
            trigger=TRIGGER_USER_REQUEST,
            restored_files=["/tmp/a.txt"],
            removed_created_files=["/tmp/b.txt"],
            verification_status=GUARD_FAILED,
            status=SESSION_STATUS_ROLLBACK_FAILED,
            warnings=["issue"],
            errors=["failed"],
        )
        assert r.rollback_id == "rb-1"
        assert r.trigger == TRIGGER_USER_REQUEST
        assert r.verification_status == GUARD_FAILED
        assert r.status == SESSION_STATUS_ROLLBACK_FAILED


class TestImplementationSession:
    def test_default_fields(self):
        s = ImplementationSession()
        assert s.session_id == ""
        assert s.proposal_id is None
        assert s.governance_decision_id is None
        assert s.policy_decision_id is None
        assert s.sandbox_decision_ids == []
        assert s.dry_run_id is None
        assert s.rollback_snapshot_id is None
        assert s.patch_application_id is None
        assert s.source_inventory_before_id is None
        assert s.source_inventory_after_id is None
        assert s.source_change_guard_id is None
        assert s.validation_result_id is None
        assert s.rollback_record_id is None
        assert s.target_paths == []
        assert s.changed_paths == []
        assert s.lifecycle_state == "CREATED"
        assert s.status == SESSION_STATUS_CREATED
        assert s.final_decision == FINAL_PENDING
        assert s.timestamp == ""
        assert s.source_component == SOURCE_COMPONENT
        assert s.warnings == []
        assert s.errors == []

    def test_custom_values(self):
        s = ImplementationSession(
            session_id="sess-1",
            proposal_id="prop-1",
            governance_decision_id="gov-1",
            policy_decision_id="pol-1",
            sandbox_decision_ids=["sand-1"],
            dry_run_id="dry-1",
            rollback_snapshot_id="snap-1",
            patch_application_id="app-1",
            source_inventory_before_id="inv-b",
            source_inventory_after_id="inv-a",
            source_change_guard_id="guard-1",
            validation_result_id="val-1",
            rollback_record_id="rb-1",
            target_paths=["/tmp/a.txt"],
            changed_paths=["/tmp/a.txt"],
            lifecycle_state="ACCEPTED",
            status=SESSION_STATUS_ACCEPTED,
            final_decision=FINAL_ACCEPT,
            timestamp="2024-01-01T00:00:00",
            source_component="Custom",
            warnings=["slow"],
            errors=[],
        )
        assert s.session_id == "sess-1"
        assert s.status == SESSION_STATUS_ACCEPTED
        assert s.final_decision == FINAL_ACCEPT
        assert s.lifecycle_state == "ACCEPTED"


class TestSourceChangeGuardResult:
    def test_default_fields(self):
        g = SourceChangeGuardResult()
        assert g.guard_id == ""
        assert g.session_id == ""
        assert g.timestamp == ""
        assert g.source_component == "SourceChangeGuard"
        assert g.approved_paths == []
        assert g.actual_changed_paths == []
        assert g.unexpected_paths == []
        assert g.missing_expected_paths == []
        assert g.forbidden_paths == []
        assert g.status == GUARD_PASS
        assert g.warnings == []
        assert g.errors == []

    def test_custom_values(self):
        g = SourceChangeGuardResult(
            guard_id="guard-1",
            session_id="sess-1",
            timestamp="2024-01-01T00:00:00",
            source_component="CustomGuard",
            approved_paths=["/tmp/a.txt"],
            actual_changed_paths=["/tmp/a.txt"],
            unexpected_paths=["/tmp/b.txt"],
            missing_expected_paths=["/tmp/c.txt"],
            forbidden_paths=["/tmp/L0/x.txt"],
            status=GUARD_BLOCKED,
            warnings=["unexpected"],
            errors=["blocked"],
        )
        assert g.guard_id == "guard-1"
        assert g.status == GUARD_BLOCKED
        assert len(g.forbidden_paths) == 1

    def test_guard_pass_status(self):
        g = SourceChangeGuardResult(status=GUARD_PASS)
        assert g.status == GUARD_PASS

    def test_guard_blocked_status(self):
        g = SourceChangeGuardResult(status=GUARD_BLOCKED)
        assert g.status == GUARD_BLOCKED

    def test_guard_failed_status(self):
        g = SourceChangeGuardResult(status=GUARD_FAILED)
        assert g.status == GUARD_FAILED


class TestImplementationValidationGateResult:
    def test_default_fields(self):
        v = ImplementationValidationGateResult()
        assert v.validation_gate_id == ""
        assert v.session_id == ""
        assert v.timestamp == ""
        assert v.source_component == "ImplementationValidationGate"
        assert v.commands_requested == []
        assert v.commands_allowed == []
        assert v.commands_blocked == []
        assert v.validation_status == VALIDATION_SKIPPED
        assert v.requires_rollback is False
        assert v.reason == ""
        assert v.warnings == []
        assert v.errors == []

    def test_custom_values(self):
        v = ImplementationValidationGateResult(
            validation_gate_id="vg-1",
            session_id="sess-1",
            timestamp="2024-01-01T00:00:00",
            source_component="CustomGate",
            commands_requested=["pytest"],
            commands_allowed=["pytest"],
            commands_blocked=["bash"],
            validation_status=VALIDATION_PASS,
            requires_rollback=False,
            reason="all good",
            warnings=[],
            errors=[],
        )
        assert v.validation_gate_id == "vg-1"
        assert v.validation_status == VALIDATION_PASS
        assert v.reason == "all good"

    def test_validation_failed_status(self):
        v = ImplementationValidationGateResult(validation_status=VALIDATION_FAILED)
        assert v.validation_status == VALIDATION_FAILED

    def test_validation_blocked_status(self):
        v = ImplementationValidationGateResult(validation_status=VALIDATION_BLOCKED)
        assert v.validation_status == VALIDATION_BLOCKED


class TestPatchExecutionDecision:
    def test_default_fields(self):
        d = PatchExecutionDecision()
        assert d.decision_id == ""
        assert d.session_id is None
        assert d.timestamp == ""
        assert d.source_component == "GovernedPatchExecution"
        assert d.decision == "PENDING"
        assert d.reason == ""
        assert d.required_actions == []
        assert d.warnings == []
        assert d.errors == []
        assert d.schema_version == "1.0"
        assert d.schema_id == "patch_execution_decision.schema.json"

    def test_custom_values(self):
        d = PatchExecutionDecision(
            decision_id="dec-1",
            session_id="sess-1",
            timestamp="2024-01-01T00:00:00",
            source_component="Custom",
            decision=FINAL_ACCEPT,
            reason="all good",
            required_actions=["notify"],
            warnings=[],
            errors=[],
        )
        assert d.decision_id == "dec-1"
        assert d.decision == FINAL_ACCEPT
        assert d.reason == "all good"


class TestPatchExecutionAuditEvent:
    def test_default_fields(self):
        e = PatchExecutionAuditEvent()
        assert e.audit_id == ""
        assert e.timestamp == ""
        assert e.source_component == SOURCE_COMPONENT
        assert e.event_type == ""
        assert e.session_id == ""
        assert e.decision == ""
        assert e.artifacts == []
        assert e.warnings == []
        assert e.errors == []

    def test_custom_values(self):
        e = PatchExecutionAuditEvent(
            audit_id="audit-1",
            timestamp="2024-01-01T00:00:00",
            source_component="Custom",
            event_type="SESSION_ACCEPTED",
            session_id="sess-1",
            decision="ACCEPT",
            artifacts=["/tmp/evidence.json"],
            warnings=[],
            errors=[],
        )
        assert e.audit_id == "audit-1"
        assert e.event_type == "SESSION_ACCEPTED"
        assert e.decision == "ACCEPT"


class TestDryRunResult:
    def test_default_fields(self):
        d = DryRunResult()
        assert d.dry_run_id == ""
        assert d.session_id == ""
        assert d.timestamp == ""
        assert d.source_component == SOURCE_COMPONENT
        assert d.would_change_paths == []
        assert d.would_create_paths == []
        assert d.would_delete_paths == []
        assert d.sandbox_decision_ids == []
        assert d.policy_decision_id is None
        assert d.rollback_required is True
        assert d.validation_plan == []
        assert d.status == GUARD_PASS
        assert d.warnings == []
        assert d.errors == []

    def test_custom_values(self):
        d = DryRunResult(
            dry_run_id="dry-1",
            session_id="sess-1",
            timestamp="2024-01-01T00:00:00",
            source_component="Custom",
            would_change_paths=["/tmp/a.txt"],
            would_create_paths=["/tmp/b.txt"],
            would_delete_paths=["/tmp/c.txt"],
            sandbox_decision_ids=["sand-1"],
            policy_decision_id="pol-1",
            rollback_required=False,
            validation_plan=["pytest"],
            status=GUARD_BLOCKED,
            warnings=["issue"],
            errors=[],
        )
        assert d.dry_run_id == "dry-1"
        assert d.rollback_required is False
        assert d.status == GUARD_BLOCKED
        assert d.policy_decision_id == "pol-1"


class TestSourceInventory:
    def test_default_fields(self):
        s = SourceInventory()
        assert s.inventory_id == ""
        assert s.session_id == ""
        assert s.timestamp == ""
        assert s.source_component == "SourceChangeGuard"
        assert s.scope == "BEFORE"
        assert s.tracked_paths == []
        assert s.path_hashes == {}
        assert s.git_status_short is None
        assert s.warnings == []
        assert s.errors == []

    def test_custom_values(self):
        s = SourceInventory(
            inventory_id="inv-1",
            session_id="sess-1",
            timestamp="2024-01-01T00:00:00",
            source_component="CustomGuard",
            scope="AFTER",
            tracked_paths=["/tmp/a.txt"],
            path_hashes={"/tmp/a.txt": "abc"},
            git_status_short="clean",
            warnings=[],
            errors=[],
        )
        assert s.inventory_id == "inv-1"
        assert s.scope == "AFTER"
        assert s.git_status_short == "clean"


class TestTemporaryPolicyBridge:
    def test_default_fields(self):
        b = TemporaryPolicyBridge()
        assert b.policy_bridge_id == ""
        assert b.timestamp == ""
        assert b.source_component == SOURCE_COMPONENT
        assert b.mode == "TEMPORARY_FAIL_CLOSED"
        assert b.allowed_roles == []
        assert b.allowed_operations == [OP_EXACT_EDIT, OP_WRITE_FILE, OP_CREATE_FILE, OP_PATCH_TEXT]
        assert b.allowed_paths == []
        assert b.blocked_paths == []
        assert b.requires_governance is True
        assert b.requires_rollback is True
        assert b.status == "ACTIVE"
        assert b.warnings == []
        assert b.errors == []

    def test_custom_values(self):
        b = TemporaryPolicyBridge(
            policy_bridge_id="pb-1",
            timestamp="2024-01-01T00:00:00",
            source_component="Custom",
            mode="TEMPORARY_FAIL_OPEN",
            allowed_roles=["admin"],
            allowed_operations=[OP_EXACT_EDIT],
            allowed_paths=["/tmp/src"],
            blocked_paths=["/tmp/L0"],
            requires_governance=False,
            requires_rollback=False,
            status="EXPIRED",
            warnings=[],
            errors=[],
        )
        assert b.policy_bridge_id == "pb-1"
        assert b.mode == "TEMPORARY_FAIL_OPEN"
        assert b.requires_governance is False
        assert b.status == "EXPIRED"
        assert b.allowed_operations == [OP_EXACT_EDIT]


class TestPatchLimits:
    def test_default_fields(self):
        p = PatchLimits()
        assert p.limits_id == ""
        assert p.timestamp == ""
        assert p.source_component == SOURCE_COMPONENT
        assert p.max_changed_files_per_session == 5
        assert p.max_patch_operations_per_session == 20
        assert p.max_single_file_bytes == 1048576
        assert p.max_patch_text_bytes == 262144
        assert p.max_total_snapshot_bytes == 10485760
        assert p.max_validation_runtime_seconds == 120
        assert p.max_session_runtime_seconds == 300
        assert p.status == "ACTIVE"
        assert p.warnings == []
        assert p.errors == []

    def test_default_limits_match_default_limits(self):
        p = PatchLimits()
        assert p.max_changed_files_per_session == DEFAULT_LIMITS["max_changed_files_per_session"]
        assert p.max_patch_operations_per_session == DEFAULT_LIMITS["max_patch_operations_per_session"]
        assert p.max_single_file_bytes == DEFAULT_LIMITS["max_single_file_bytes"]
        assert p.max_patch_text_bytes == DEFAULT_LIMITS["max_patch_text_bytes"]
        assert p.max_total_snapshot_bytes == DEFAULT_LIMITS["max_total_snapshot_bytes"]
        assert p.max_validation_runtime_seconds == DEFAULT_LIMITS["max_validation_runtime_seconds"]
        assert p.max_session_runtime_seconds == DEFAULT_LIMITS["max_session_runtime_seconds"]

    def test_custom_values(self):
        p = PatchLimits(
            limits_id="lim-1",
            timestamp="2024-01-01T00:00:00",
            source_component="Custom",
            max_changed_files_per_session=10,
            max_patch_operations_per_session=50,
            max_single_file_bytes=4096,
            max_patch_text_bytes=1024,
            max_total_snapshot_bytes=99999,
            max_validation_runtime_seconds=60,
            max_session_runtime_seconds=600,
            status="DISABLED",
            warnings=["limit low"],
            errors=[],
        )
        assert p.limits_id == "lim-1"
        assert p.max_changed_files_per_session == 10
        assert p.max_session_runtime_seconds == 600
        assert p.status == "DISABLED"
