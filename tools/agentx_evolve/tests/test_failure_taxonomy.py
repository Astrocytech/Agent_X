import pytest
import json
from pathlib import Path
from agentx_evolve.failure.failure_models import (
    FailureEvent, FailureReport, FailureCategory, FailureSeverity,
    RecoveryAction, RecoveryPlaybook,
    CAT_PATH_BOUNDARY, CAT_GOVERNANCE_BLOCKED, CAT_VALIDATION_FAILED,
    CAT_SUBPROCESS_BLOCKED, CAT_NETWORK_BLOCKED, CAT_SANDBOX_VIOLATION,
    CAT_POLICY_BLOCKED, CAT_PATCH_APPLY_FAILED, CAT_ROLLBACK_FAILED,
    CAT_INTERNAL_ERROR,
    SEV_LOW, SEV_MEDIUM, SEV_HIGH, SEV_CRITICAL,
    ACTION_RETRY, ACTION_ROLLBACK, ACTION_ESCALATE, ACTION_REPROPOSE,
    ACTION_ADJUST_POLICY, ACTION_SKIP, ACTION_REVIEW,
    ALL_CATEGORIES, ALL_SEVERITIES, ALL_ACTIONS,
    new_id, utc_now_iso, to_dict,
)
from agentx_evolve.failure.failure_classifier import FailureClassifier
from agentx_evolve.failure.recovery_playbook import (
    RecoveryPlaybookManager, default_playbooks,
)
from agentx_evolve.failure.failure_evidence import FailureEvidenceWriter


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def classifier():
    return FailureClassifier()


@pytest.fixture
def playbook_manager():
    return RecoveryPlaybookManager()


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    (r / ".agentx-init").mkdir()
    return r


@pytest.fixture
def evidence_writer(repo):
    return FailureEvidenceWriter(repo)


@pytest.fixture
def sample_event():
    return FailureEvent(
        event_id="fail-001",
        session_id="sess-001",
        category=CAT_PATH_BOUNDARY,
        severity=SEV_HIGH,
        source_component="PathBoundary",
        summary="Path outside repository boundaries",
    )


# ---------------------------------------------------------------------------
# FailureEvent tests
# ---------------------------------------------------------------------------

def test_failure_event_defaults():
    event = FailureEvent()
    assert event.category == CAT_INTERNAL_ERROR
    assert event.severity == SEV_MEDIUM
    assert not event.recovered


def test_failure_event_custom(sample_event):
    assert sample_event.event_id == "fail-001"
    assert sample_event.category == CAT_PATH_BOUNDARY
    assert sample_event.severity == SEV_HIGH


def test_failure_event_to_dict(sample_event):
    d = sample_event.to_dict()
    assert d["event_id"] == "fail-001"
    assert d["category"] == CAT_PATH_BOUNDARY


def test_failure_event_mark_recovered(sample_event):
    sample_event.recovered = True
    assert sample_event.recovered


# ---------------------------------------------------------------------------
# FailureReport tests
# ---------------------------------------------------------------------------

def test_failure_report_defaults():
    report = FailureReport()
    assert report.events == []
    assert report.event_count() == 0


def test_failure_report_add_event(sample_event):
    report = FailureReport()
    report.add_event(sample_event)
    assert report.event_count() == 1


def test_failure_report_add_multiple():
    report = FailureReport()
    report.add_event(FailureEvent(category=CAT_PATH_BOUNDARY))
    report.add_event(FailureEvent(category=CAT_GOVERNANCE_BLOCKED))
    assert report.event_count() == 2


def test_failure_report_events_by_category():
    report = FailureReport()
    report.add_event(FailureEvent(category=CAT_PATH_BOUNDARY))
    report.add_event(FailureEvent(category=CAT_PATH_BOUNDARY))
    report.add_event(FailureEvent(category=CAT_GOVERNANCE_BLOCKED))
    assert len(report.events_by_category(CAT_PATH_BOUNDARY)) == 2
    assert len(report.events_by_category(CAT_GOVERNANCE_BLOCKED)) == 1


def test_failure_report_events_by_severity():
    report = FailureReport()
    report.add_event(FailureEvent(severity=SEV_HIGH))
    report.add_event(FailureEvent(severity=SEV_LOW))
    assert len(report.events_by_severity(SEV_HIGH)) == 1
    assert len(report.events_by_severity(SEV_LOW)) == 1


def test_failure_report_highest_severity():
    report = FailureReport()
    report.add_event(FailureEvent(severity=SEV_LOW))
    report.add_event(FailureEvent(severity=SEV_CRITICAL))
    assert report.highest_severity() == SEV_CRITICAL


def test_failure_report_highest_severity_empty():
    report = FailureReport()
    assert report.highest_severity() == SEV_LOW


def test_failure_report_unrecovered_count():
    report = FailureReport()
    e1 = FailureEvent(category=CAT_PATH_BOUNDARY, recovered=True)
    e2 = FailureEvent(category=CAT_GOVERNANCE_BLOCKED, recovered=False)
    report.add_event(e1)
    report.add_event(e2)
    assert report.unrecovered_count() == 1


def test_failure_report_generate_summary():
    report = FailureReport()
    report.add_event(FailureEvent(category=CAT_PATH_BOUNDARY, severity=SEV_HIGH))
    report.add_event(FailureEvent(category=CAT_GOVERNANCE_BLOCKED, severity=SEV_LOW))
    summary = report.generate_summary()
    assert summary["total_events"] == 2
    assert summary["highest_severity"] == SEV_HIGH
    assert CAT_PATH_BOUNDARY in summary["by_category"]


def test_failure_report_to_dict():
    report = FailureReport(report_id="r1")
    report.add_event(FailureEvent(event_id="e1"))
    d = report.to_dict()
    assert d["report_id"] == "r1"
    assert len(d["events"]) == 1


# ---------------------------------------------------------------------------
# RecoveryAction tests
# ---------------------------------------------------------------------------

def test_recovery_action_defaults():
    action = RecoveryAction()
    assert action.action_type == ACTION_RETRY
    assert not action.requires_approval


def test_recovery_action_custom():
    action = RecoveryAction(
        action_type=ACTION_ROLLBACK,
        description="Roll back changes",
        requires_approval=True,
    )
    assert action.action_type == ACTION_ROLLBACK
    assert action.requires_approval


def test_recovery_action_to_dict():
    action = RecoveryAction(action_id="ra-1", action_type=ACTION_SKIP)
    d = action.to_dict()
    assert d["action_id"] == "ra-1"
    assert d["action_type"] == ACTION_SKIP


# ---------------------------------------------------------------------------
# RecoveryPlaybook tests
# ---------------------------------------------------------------------------

def test_recovery_playbook_defaults():
    pb = RecoveryPlaybook()
    assert pb.failure_category == ""
    assert pb.severity == SEV_MEDIUM
    assert not pb.auto_recoverable
    assert pb.suggested_actions == []


def test_recovery_playbook_with_actions():
    actions = [
        RecoveryAction(action_type=ACTION_RETRY),
        RecoveryAction(action_type=ACTION_ROLLBACK, requires_approval=True),
    ]
    pb = RecoveryPlaybook(
        playbook_id="pb-test",
        failure_category=CAT_VALIDATION_FAILED,
        severity=SEV_HIGH,
        suggested_actions=actions,
    )
    assert len(pb.suggested_actions) == 2
    assert pb.failure_category == CAT_VALIDATION_FAILED


def test_recovery_playbook_to_dict():
    pb = RecoveryPlaybook(playbook_id="pb-1", failure_category=CAT_PATH_BOUNDARY)
    d = pb.to_dict()
    assert d["playbook_id"] == "pb-1"
    assert d["failure_category"] == CAT_PATH_BOUNDARY


# ---------------------------------------------------------------------------
# FailureClassifier tests
# ---------------------------------------------------------------------------

def test_classify_path_boundary(classifier):
    event = classifier.classify("L0 writes are always blocked", "PathBoundary")
    assert event.category == CAT_PATH_BOUNDARY


def test_classify_governance_blocked(classifier):
    event = classifier.classify("Governance decision ID is required", "FileChangeGuard")
    assert event.category == CAT_GOVERNANCE_BLOCKED


def test_classify_validation_failed(classifier):
    event = classifier.classify("Validation failed: compilation error", "ValidationGate")
    assert event.category == CAT_VALIDATION_FAILED


def test_classify_subprocess_blocked(classifier):
    event = classifier.classify("subprocess command blocked by policy", "SafeSubprocess")
    assert event.category == CAT_SUBPROCESS_BLOCKED


def test_classify_network_blocked(classifier):
    event = classifier.classify("Network not allowed by policy", "NetworkPolicy")
    assert event.category == CAT_NETWORK_BLOCKED


def test_classify_sandbox_violation(classifier):
    event = classifier.classify("sandbox violation detected", "SecuritySandbox")
    assert event.category == CAT_SANDBOX_VIOLATION


def test_classify_policy_blocked(classifier):
    event = classifier.classify("not registered in capability registry", "PolicyEnforcer")
    assert event.category == CAT_POLICY_BLOCKED


def test_classify_patch_apply_failed_old_text_not_found(classifier):
    event = classifier.classify("OLD_TEXT_NOT_FOUND: old_text does not appear in file", "PatchApplier")
    assert event.category == CAT_PATCH_APPLY_FAILED


def test_classify_patch_apply_failed_write_error(classifier):
    event = classifier.classify("Write error: permission denied", "PatchApplier")
    assert event.category == CAT_PATCH_APPLY_FAILED


def test_classify_rollback_failed(classifier):
    event = classifier.classify("rollback snapshot not found", "RollbackManager")
    assert event.category == CAT_ROLLBACK_FAILED


def test_classify_internal_error(classifier):
    event = classifier.classify("internal error: unexpected exception", "Component")
    assert event.category == CAT_INTERNAL_ERROR


def test_classify_unknown_reason(classifier):
    event = classifier.classify("something completely unknown", "Component")
    assert event.category == CAT_INTERNAL_ERROR


def test_classify_sandbox_decision_method(classifier):
    event = classifier.classify_sandbox_decision("L0 path blocked")
    assert event.source_component == "SecuritySandbox"


def test_classify_governance_method(classifier):
    event = classifier.classify_governance_block("No governance ID")
    assert event.source_component == "FileChangeGuard"


def test_classify_validation_method(classifier):
    event = classifier.classify_validation_failure("Validation failed")
    assert event.source_component == "ImplementationValidationGate"


def test_classify_patch_method(classifier):
    event = classifier.classify_patch_failure("Patch apply error")
    assert event.source_component == "PatchApplier"


def test_classify_rollback_method(classifier):
    event = classifier.classify_rollback_failure("Rollback error")
    assert event.source_component == "RollbackManager"


def test_classify_policy_method(classifier):
    event = classifier.classify_policy_block("Not allowed by policy")
    assert event.source_component == "PolicyEnforcer"


def test_classify_suggested_action_path_boundary(classifier):
    event = classifier.classify("L0_BLOCK: L0 write")
    assert event.suggested_action == ACTION_SKIP


def test_classify_suggested_action_governance(classifier):
    event = classifier.classify("governance decision required")
    assert event.suggested_action == ACTION_REPROPOSE


def test_classify_suggested_action_sandbox(classifier):
    event = classifier.classify("blocked by sandbox")
    assert event.suggested_action == ACTION_ESCALATE


def test_classify_severity_critical_for_rollback(classifier):
    event = classifier.classify("rollback failed")
    assert event.severity == SEV_CRITICAL


def test_classify_severity_low_for_network(classifier):
    event = classifier.classify("Network not allowed")
    assert event.severity == SEV_LOW


# ---------------------------------------------------------------------------
# RecoveryPlaybookManager tests
# ---------------------------------------------------------------------------

def test_playbook_manager_defaults(playbook_manager):
    pbs = playbook_manager.playbooks
    assert len(pbs) == 10
    cats = {pb.failure_category for pb in pbs}
    assert CAT_PATH_BOUNDARY in cats
    assert CAT_INTERNAL_ERROR in cats


def test_playbook_manager_get_playbook(playbook_manager):
    pb = playbook_manager.get_playbook(CAT_PATH_BOUNDARY)
    assert pb is not None
    assert pb.failure_category == CAT_PATH_BOUNDARY


def test_playbook_manager_get_playbook_not_found(playbook_manager):
    pb = playbook_manager.get_playbook("NONEXISTENT")
    assert pb is None


def test_playbook_manager_get_suggested_actions(playbook_manager):
    actions = playbook_manager.get_suggested_actions(CAT_VALIDATION_FAILED)
    assert len(actions) >= 2


def test_playbook_manager_get_suggested_actions_not_found(playbook_manager):
    assert playbook_manager.get_suggested_actions("GHOST") == []


def test_playbook_manager_add_playbook(playbook_manager):
    new_pb = RecoveryPlaybook(playbook_id="pb-custom", failure_category="CUSTOM")
    playbook_manager.add_playbook(new_pb)
    assert playbook_manager.get_playbook("CUSTOM") is not None


def test_playbook_manager_remove_playbook(playbook_manager):
    assert playbook_manager.remove_playbook(CAT_PATH_BOUNDARY)
    assert playbook_manager.get_playbook(CAT_PATH_BOUNDARY) is None


def test_playbook_manager_remove_not_found(playbook_manager):
    assert not playbook_manager.remove_playbook("GHOST")


def test_playbook_manager_is_auto_recoverable(playbook_manager):
    assert playbook_manager.is_auto_recoverable(CAT_GOVERNANCE_BLOCKED)
    assert not playbook_manager.is_auto_recoverable(CAT_PATH_BOUNDARY)


def test_playbook_manager_is_auto_recoverable_not_found(playbook_manager):
    assert not playbook_manager.is_auto_recoverable("GHOST")


def test_playbook_manager_categories(playbook_manager):
    cats = playbook_manager.categories()
    assert len(cats) == 10
    assert CAT_INTERNAL_ERROR in cats


def test_default_playbooks_count():
    pbs = default_playbooks()
    assert len(pbs) == 10


def test_default_playbooks_content():
    pbs = default_playbooks()
    for pb in pbs:
        assert pb.playbook_id
        assert pb.failure_category
        assert pb.severity
        assert len(pb.suggested_actions) >= 1


# ---------------------------------------------------------------------------
# FailureEvidenceWriter tests
# ---------------------------------------------------------------------------

def test_evidence_writer_write_event(evidence_writer, sample_event):
    result = evidence_writer.write_event(sample_event)
    assert result["status"] == "APPENDED"
    path = evidence_writer.get_event_log_path()
    assert path.exists()
    content = path.read_text()
    assert sample_event.event_id in content


def test_evidence_writer_write_event_appends(evidence_writer):
    evidence_writer.write_event(FailureEvent(event_id="e1"))
    evidence_writer.write_event(FailureEvent(event_id="e2"))
    path = evidence_writer.get_event_log_path()
    lines = [l for l in path.read_text().strip().split("\n") if l]
    assert len(lines) == 2


def test_evidence_writer_write_report(evidence_writer):
    report = FailureReport(report_id="r1")
    report.add_event(FailureEvent(event_id="e1"))
    result = evidence_writer.write_report(report)
    assert result["status"] == "APPENDED"
    path = evidence_writer.get_report_log_path()
    assert path.exists()


def test_evidence_writer_write_latest_events(evidence_writer):
    events = [
        FailureEvent(event_id="e1"),
        FailureEvent(event_id="e2"),
    ]
    result = evidence_writer.write_latest_events(events)
    assert result["status"] == "WRITTEN"
    path = evidence_writer.get_latest_path()
    assert path.exists()
    data = json.loads(path.read_text())
    assert len(data["events"]) == 2


def test_evidence_writer_creates_dir(repo):
    writer = FailureEvidenceWriter(repo)
    writer.write_event(FailureEvent(event_id="e1"))
    assert (repo / ".agentx-init" / "failures").exists()


# ---------------------------------------------------------------------------
# Enums and constants tests
# ---------------------------------------------------------------------------

def test_all_categories():
    assert len(ALL_CATEGORIES) == 10
    assert CAT_PATH_BOUNDARY in ALL_CATEGORIES
    assert CAT_INTERNAL_ERROR in ALL_CATEGORIES


def test_all_severities():
    assert len(ALL_SEVERITIES) == 4
    assert SEV_LOW in ALL_SEVERITIES
    assert SEV_CRITICAL in ALL_SEVERITIES


def test_all_actions():
    assert len(ALL_ACTIONS) == 7
    assert ACTION_RETRY in ALL_ACTIONS
    assert ACTION_REVIEW in ALL_ACTIONS


def test_failure_category_enum():
    assert FailureCategory.PATH_BOUNDARY_VIOLATION.value == CAT_PATH_BOUNDARY
    assert FailureCategory.INTERNAL_ERROR.value == CAT_INTERNAL_ERROR


def test_failure_severity_enum():
    assert FailureSeverity.LOW.value == SEV_LOW
    assert FailureSeverity.CRITICAL.value == SEV_CRITICAL


def test_to_dict_with_enum():
    event = FailureEvent(category=CAT_PATH_BOUNDARY, severity=SEV_HIGH)
    d = event.to_dict()
    assert d["category"] == CAT_PATH_BOUNDARY
    assert d["severity"] == SEV_HIGH


# ---------------------------------------------------------------------------
# Helper tests
# ---------------------------------------------------------------------------

def test_helper_new_id():
    nid = new_id("fail")
    assert nid.startswith("fail-")
    assert len(nid) > 5


def test_helper_utc_now_iso():
    iso = utc_now_iso()
    assert "T" in iso


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_report_summary():
    report = FailureReport()
    summary = report.generate_summary()
    assert summary["total_events"] == 0
    assert summary["highest_severity"] == SEV_LOW


def test_classify_with_session_id(classifier):
    event = classifier.classify("L0 path blocked", session_id="sess-001")
    assert event.session_id == "sess-001"


def test_classify_empty_reason(classifier):
    event = classifier.classify("")
    assert event.category == CAT_INTERNAL_ERROR


def test_recovery_action_with_command():
    action = RecoveryAction(
        action_type=ACTION_RETRY,
        command=["python3", "-c", "print('retry')"],
    )
    assert len(action.command) == 3


def test_failure_event_serialization_roundtrip(sample_event):
    d = sample_event.to_dict()
    restored = FailureEvent(**d)
    assert restored.event_id == sample_event.event_id
    assert restored.category == sample_event.category
    assert restored.severity == sample_event.severity


def test_playbook_manager_construction_with_custom():
    custom_pbs = [
        RecoveryPlaybook(playbook_id="pb-a", failure_category="A"),
        RecoveryPlaybook(playbook_id="pb-b", failure_category="B"),
    ]
    manager = RecoveryPlaybookManager(custom_pbs)
    assert len(manager.playbooks) == 2
    assert manager.get_playbook("A") is not None


def test_evidence_writer_get_paths(evidence_writer):
    assert str(evidence_writer.get_event_log_path()).endswith("failure_events.jsonl")
    assert str(evidence_writer.get_report_log_path()).endswith("failure_reports.jsonl")
    assert str(evidence_writer.get_latest_path()).endswith("failure_latest.json")
