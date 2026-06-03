import pytest
import json
import os
import subprocess
from pathlib import Path
from agentx_evolve.patch.patch_models import (
    PatchSession, PatchAction, RollbackSnapshot,
    ImplementationEvidence, ImplementationSessionStatus,
    SESSION_CREATED, SESSION_LOADED, SESSION_PROPOSAL_LOADED,
    SESSION_GOVERNANCE_CHECKED, SESSION_PATCH_APPLIED,
    SESSION_VALIDATED, SESSION_ACCEPTED, SESSION_ROLLED_BACK,
    SESSION_FAILED, SESSION_BLOCKED,
    ACTION_UPDATE, ACTION_CREATE, ACTION_DELETE,
    utc_now_iso, new_id, sha256_text, sha256_file, to_dict,
    _validate_transition, VALID_TRANSITIONS,
)
from agentx_evolve.patch.file_change_guard import FileChangeGuard
from agentx_evolve.patch.git_diff_guard import GitDiffGuard
from agentx_evolve.patch.rollback_manager import RollbackManager
from agentx_evolve.patch.patch_applier import PatchApplier
from agentx_evolve.patch.implementation_session import ImplementationSession
from agentx_evolve.patch.implementation_evidence import ImplementationEvidenceWriter
from agentx_evolve.patch.implementation_validation_gate import ImplementationValidationGate
from agentx_evolve.security.sandbox_policy import default_sandbox_policy, merge_sandbox_policy
from agentx_evolve.security.security_models import (
    SandboxPolicy, SandboxDecision,
    DECISION_ALLOW, DECISION_BLOCK, STATUS_SUCCESS,
    OP_EDIT, OP_WRITE,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    (r / "L0").mkdir()
    (r / "L0" / "protected.py").write_text("original l0 content")
    (r / "src").mkdir()
    (r / "src" / "greeting.py").write_text("def hello():\n    return 'hello'\n")
    (r / "src" / "config.txt").write_text("setting=old\n")
    (r / ".agentx-init").mkdir()
    return r


@pytest.fixture
def default_policy(repo):
    return default_sandbox_policy(repo)


@pytest.fixture
def source_write_policy(repo):
    return merge_sandbox_policy(default_sandbox_policy(repo), {
        "source_write_allowed": True,
        "allowlisted_write_paths": [".agentx-init/", "src/"],
    })


@pytest.fixture
def file_guard(repo, default_policy):
    return FileChangeGuard(repo, default_policy)


@pytest.fixture
def session(repo, source_write_policy):
    return ImplementationSession(
        repo_root=repo,
        policy=source_write_policy,
        proposal_id="prop-001",
        governance_decision_id="gov-001",
        risk_assessment_id="risk-001",
    )


# ---------------------------------------------------------------------------
# PatchModels — state machine
# ---------------------------------------------------------------------------

def test_validate_transition_valid():
    assert _validate_transition(SESSION_CREATED, SESSION_LOADED) == SESSION_LOADED


def test_validate_transition_invalid():
    with pytest.raises(ValueError, match="Invalid state transition"):
        _validate_transition(SESSION_CREATED, SESSION_ACCEPTED)


def test_session_status_initial():
    s = ImplementationSessionStatus()
    assert s.current == SESSION_CREATED
    assert s.history == []


def test_session_status_transition():
    s = ImplementationSessionStatus()
    s.transition_to(SESSION_LOADED)
    assert s.current == SESSION_LOADED
    assert len(s.history) == 1
    assert s.history[0]["from"] == SESSION_CREATED
    assert s.history[0]["to"] == SESSION_LOADED


def test_session_status_invalid_transition():
    s = ImplementationSessionStatus()
    with pytest.raises(ValueError):
        s.transition_to(SESSION_ACCEPTED)


def test_accept_is_terminal():
    s = ImplementationSessionStatus()
    s.transition_to(SESSION_LOADED)
    s.transition_to(SESSION_PROPOSAL_LOADED)
    s.transition_to(SESSION_GOVERNANCE_CHECKED)
    s.transition_to(SESSION_PATCH_APPLIED)
    s.transition_to(SESSION_VALIDATED)
    s.transition_to(SESSION_ACCEPTED)
    assert s.current == SESSION_ACCEPTED
    assert len(s.history) == 6


def test_rolled_back_is_terminal():
    s = ImplementationSessionStatus()
    s.transition_to(SESSION_LOADED)
    s.transition_to(SESSION_PROPOSAL_LOADED)
    s.transition_to(SESSION_GOVERNANCE_CHECKED)
    s.transition_to(SESSION_PATCH_APPLIED)
    s.transition_to(SESSION_ROLLED_BACK)
    assert s.current == SESSION_ROLLED_BACK


def test_failed_is_terminal():
    s = ImplementationSessionStatus()
    s.transition_to(SESSION_LOADED)
    s.transition_to(SESSION_FAILED)
    assert s.current == SESSION_FAILED


def test_blocked_is_terminal():
    s = ImplementationSessionStatus()
    s.transition_to(SESSION_BLOCKED)
    assert s.current == SESSION_BLOCKED


def test_from_loaded_allowed_transitions():
    allowed = set(VALID_TRANSITIONS[SESSION_LOADED])
    assert SESSION_PROPOSAL_LOADED in allowed


def test_from_validated_allowed_transitions():
    allowed = set(VALID_TRANSITIONS[SESSION_VALIDATED])
    assert SESSION_ACCEPTED in allowed
    assert SESSION_ROLLED_BACK in allowed


def test_from_patch_applied_allowed_transitions():
    allowed = set(VALID_TRANSITIONS[SESSION_PATCH_APPLIED])
    assert SESSION_VALIDATED in allowed
    assert SESSION_ROLLED_BACK in allowed


# ---------------------------------------------------------------------------
# PatchModels — helpers
# ---------------------------------------------------------------------------

def test_utc_now_iso_format():
    iso = utc_now_iso()
    assert "T" in iso


def test_new_id_uniqueness():
    ids = {new_id() for _ in range(100)}
    assert len(ids) == 100


def test_new_id_with_prefix():
    nid = new_id("sess")
    assert nid.startswith("sess-")


def test_sha256_text_consistency():
    a = sha256_text("hello")
    b = sha256_text("hello")
    c = sha256_text("world")
    assert a == b
    assert a != c


def test_sha256_text_type():
    h = sha256_text("data")
    assert isinstance(h, str)
    assert len(h) == 64


# ---------------------------------------------------------------------------
# PatchModels — to_dict / serialization
# ---------------------------------------------------------------------------

def test_patch_action_to_dict():
    action = PatchAction(
        action_id="act-001", target_file="src/test.py",
        change_type=ACTION_UPDATE, old_text="old", new_text="new",
    )
    d = action.to_dict()
    assert d["action_id"] == "act-001"
    assert d["target_file"] == "src/test.py"
    assert d["change_type"] == ACTION_UPDATE


def test_patch_session_to_dict():
    sess = PatchSession(session_id="sess-001")
    d = sess.to_dict()
    assert d["session_id"] == "sess-001"
    assert "status" in d
    assert d["status"]["current"] == SESSION_CREATED
    assert d["actions"] == []


def test_patch_session_to_dict_with_actions():
    sess = PatchSession(session_id="sess-002")
    sess.actions.append(PatchAction(action_id="act-001", target_file="f.py"))
    d = sess.to_dict()
    assert len(d["actions"]) == 1
    assert d["actions"][0]["action_id"] == "act-001"


def test_rollback_snapshot_to_dict():
    snap = RollbackSnapshot(
        snapshot_id="snap-001",
        file_path="src/f.py",
        before_hash="abc123",
        snapshot_path="/tmp/snap.bak",
    )
    d = snap.to_dict()
    assert d["snapshot_id"] == "snap-001"
    assert d["file_path"] == "src/f.py"


def test_implementation_evidence_to_dict():
    ev = ImplementationEvidence(
        evidence_id="ev-001",
        session_id="sess-001",
        event_type="TEST",
        summary="test event",
    )
    d = ev.to_dict()
    assert d["evidence_id"] == "ev-001"
    assert d["event_type"] == "TEST"


def test_to_dict_with_dataclass_list():
    sess = PatchSession(session_id="sess-003")
    sess.actions.append(PatchAction(action_id="act-001"))
    d = to_dict(sess)
    assert len(d["actions"]) == 1


# ---------------------------------------------------------------------------
# FileChangeGuard
# ---------------------------------------------------------------------------

def test_guard_blocks_l0_path(file_guard):
    result = file_guard.check_change_allowed("L0/protected.py")
    assert result.decision == DECISION_BLOCK
    assert "L0" in result.reason


def test_guard_blocks_outside_repo(repo, default_policy):
    guard = FileChangeGuard(repo, default_policy)
    result = guard.check_change_allowed("../outside.txt")
    assert result.decision == DECISION_BLOCK


def test_guard_blocks_protected_path(repo, default_policy):
    policy = merge_sandbox_policy(default_policy, {"source_write_allowed": True})
    guard = FileChangeGuard(repo, policy)
    result = guard.check_change_allowed("core/settings.py")
    assert result.decision == DECISION_BLOCK


def test_guard_blocks_without_governance(repo, default_policy):
    policy = merge_sandbox_policy(default_policy, {"source_write_allowed": True})
    guard = FileChangeGuard(repo, policy)
    result = guard.check_change_allowed("src/greeting.py")
    assert result.decision == DECISION_BLOCK
    assert "Governance" in result.reason


def test_guard_blocks_without_session(repo, default_policy):
    policy = merge_sandbox_policy(default_policy, {"source_write_allowed": True})
    guard = FileChangeGuard(repo, policy)
    result = guard.check_change_allowed(
        "src/greeting.py", governance_decision_id="gov-001",
    )
    assert result.decision == DECISION_BLOCK
    assert "session" in result.reason


def test_guard_allows_with_governance_and_session(repo, default_policy):
    policy = merge_sandbox_policy(default_policy, {"source_write_allowed": True})
    guard = FileChangeGuard(repo, policy)
    result = guard.check_change_allowed(
        "src/greeting.py",
        implementation_session_id="sess-001",
        governance_decision_id="gov-001",
    )
    assert result.decision == DECISION_ALLOW


def test_guard_runtime_path_requires_governance(repo, default_policy):
    policy = merge_sandbox_policy(default_policy, {"source_write_allowed": True})
    guard = FileChangeGuard(repo, policy)
    result = guard.check_change_allowed(".agentx-init/test.log")
    assert result.decision == DECISION_BLOCK
    assert "Governance" in result.reason


def test_guard_runtime_path_allows_with_governance_and_session(repo, default_policy):
    policy = merge_sandbox_policy(default_policy, {"source_write_allowed": True})
    guard = FileChangeGuard(repo, policy)
    result = guard.check_change_allowed(
        ".agentx-init/test.log",
        implementation_session_id="sess-001",
        governance_decision_id="gov-001",
    )
    assert result.decision == DECISION_ALLOW


def test_verify_changed_files_no_violations():
    guard = FileChangeGuard(Path("/tmp"), default_sandbox_policy(Path("/tmp")))
    violations = guard.verify_changed_files(
        ["src/a.py", "src/b.py"],
        ["src/a.py", "src/b.py"],
    )
    assert violations == []


def test_verify_changed_files_unexpected():
    guard = FileChangeGuard(Path("/tmp"), default_sandbox_policy(Path("/tmp")))
    violations = guard.verify_changed_files(
        ["src/a.py"],
        ["src/a.py", "src/unexpected.py"],
    )
    assert any("Unexpected" in v for v in violations)


def test_verify_changed_files_missing():
    guard = FileChangeGuard(Path("/tmp"), default_sandbox_policy(Path("/tmp")))
    violations = guard.verify_changed_files(
        ["src/a.py", "src/b.py"],
        ["src/a.py"],
    )
    assert any("Expected change not found" in v for v in violations)


# ---------------------------------------------------------------------------
# GitDiffGuard (requires git repo)
# ---------------------------------------------------------------------------

@pytest.fixture
def git_repo(tmp_path):
    r = tmp_path / "git_repo"
    r.mkdir()
    subprocess.run(["git", "init"], cwd=r, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=r, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=r, capture_output=True)
    (r / "readme.md").write_text("# repo\n")
    subprocess.run(["git", "add", "."], cwd=r, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=r, capture_output=True)
    return r


def test_git_diff_guard_get_diff_name_only(git_repo):
    (git_repo / "readme.md").write_text("# modified\n")
    guard = GitDiffGuard(git_repo)
    files = guard.get_diff_name_only()
    assert "readme.md" in files


def test_git_diff_guard_get_diff(git_repo):
    (git_repo / "readme.md").write_text("# modified\n")
    guard = GitDiffGuard(git_repo)
    diff = guard.get_diff()
    assert "modified" in diff


def test_git_diff_guard_get_diff_stat(git_repo):
    (git_repo / "readme.md").write_text("# modified\n")
    guard = GitDiffGuard(git_repo)
    stat = guard.get_diff_stat()
    assert "readme.md" in stat


def test_git_diff_guard_get_diff_for_file(git_repo):
    (git_repo / "readme.md").write_text("# modified\n")
    guard = GitDiffGuard(git_repo)
    diff = guard.get_diff_for_file("readme.md")
    assert "modified" in diff


def test_git_diff_guard_has_changes_true(git_repo):
    (git_repo / "readme.md").write_text("# changes\n")
    guard = GitDiffGuard(git_repo)
    assert guard.has_changes()


def test_git_diff_guard_has_changes_false(git_repo):
    guard = GitDiffGuard(git_repo)
    assert not guard.has_changes()


def test_git_diff_guard_verify_only_expected(git_repo):
    (git_repo / "readme.md").write_text("# modified\n")
    guard = GitDiffGuard(git_repo)
    ok, unexpected = guard.verify_only_expected_files_changed({"readme.md"})
    assert ok
    assert unexpected == []


def test_git_diff_guard_verify_unexpected(git_repo):
    (git_repo / "readme.md").write_text("# modified\n")
    guard = GitDiffGuard(git_repo)
    ok, unexpected = guard.verify_only_expected_files_changed({"other.txt"})
    assert not ok
    assert "readme.md" in unexpected


def test_git_diff_guard_no_repo_graceful(tmp_path):
    guard = GitDiffGuard(tmp_path)
    assert guard.get_diff() == ""
    assert guard.get_diff_name_only() == []
    assert guard.get_diff_stat() == ""
    assert not guard.has_changes()


# ---------------------------------------------------------------------------
# RollbackManager
# ---------------------------------------------------------------------------

def test_rollback_snapshot_new_file(repo):
    manager = RollbackManager(repo)
    new_file = "src/new_rollback_test.txt"
    (repo / new_file).write_text("fresh")
    snap = manager.snapshot_file(new_file, "sess-001")
    assert snap.file_path == new_file
    assert snap.session_id == "sess-001"
    snap_path = Path(snap.snapshot_path)
    assert snap_path.exists()
    assert snap.before_hash == sha256_text("fresh")
    snap_path.unlink(missing_ok=True)


def test_rollback_snapshot_nonexistent_file(repo):
    manager = RollbackManager(repo)
    snap = manager.snapshot_file("src/ghost.txt", "sess-002")
    assert snap.before_hash == ""
    snap_path = Path(snap.snapshot_path)
    assert snap_path.exists()
    assert snap_path.read_text() == ""
    snap_path.unlink(missing_ok=True)


def test_rollback_snapshot_files(repo):
    manager = RollbackManager(repo)
    (repo / "src" / "a.txt").write_text("a")
    (repo / "src" / "b.txt").write_text("b")
    snaps = manager.snapshot_files(["src/a.txt", "src/b.txt"], "sess-003")
    assert len(snaps) == 2
    for s in snaps:
        assert Path(s.snapshot_path).exists()
        assert s.session_id == "sess-003"
    for s in snaps:
        Path(s.snapshot_path).unlink(missing_ok=True)


def test_rollback_restore_snapshot(repo):
    manager = RollbackManager(repo)
    target = "src/restore_test.txt"
    fp = repo / target
    fp.write_text("original")
    snap = manager.snapshot_file(target, "sess-004")
    fp.write_text("modified")
    result = manager.restore_snapshot(snap)
    assert result["status"] == STATUS_SUCCESS
    assert fp.read_text() == "original"


def test_rollback_restore_snapshot_nonexistent(repo):
    manager = RollbackManager(repo)
    snap = RollbackSnapshot(
        snapshot_id="bad",
        file_path="src/x.txt",
        snapshot_path="/nonexistent/bad.bak",
    )
    result = manager.restore_snapshot(snap)
    assert result["status"] == "FAILED"


def test_rollback_restore_all(repo):
    manager = RollbackManager(repo)
    (repo / "src" / "r1.txt").write_text("one")
    (repo / "src" / "r2.txt").write_text("two")
    snaps = manager.snapshot_files(["src/r1.txt", "src/r2.txt"], "sess-005")
    (repo / "src" / "r1.txt").write_text("MODIFIED")
    (repo / "src" / "r2.txt").write_text("MODIFIED")
    results = manager.restore_all(snaps)
    assert len(results) == 2
    assert all(r["status"] == STATUS_SUCCESS for r in results)
    assert (repo / "src" / "r1.txt").read_text() == "one"
    assert (repo / "src" / "r2.txt").read_text() == "two"


def test_rollback_restore_created_file(repo):
    manager = RollbackManager(repo)
    target = "src/created_file.txt"
    snap = manager.snapshot_file(target, "sess-006")
    (repo / target).write_text("i was created after snapshot")
    result = manager.restore_snapshot(snap)
    assert result["status"] == STATUS_SUCCESS
    assert not (repo / target).exists()


def test_rollback_cleanup_session(repo):
    manager = RollbackManager(repo)
    (repo / "src" / "clean.txt").write_text("data")
    manager.snapshot_file("src/clean.txt", "sess-cleanup")
    snap_dir = repo / ".agentx-init" / "implementation" / "rollback_snapshots" / "sess-cleanup"
    assert snap_dir.exists()
    result = manager.cleanup_session("sess-cleanup")
    assert result["status"] == STATUS_SUCCESS
    assert not snap_dir.exists()


def test_rollback_cleanup_nonexistent(repo):
    manager = RollbackManager(repo)
    result = manager.cleanup_session("nonexistent-session")
    assert result["status"] == STATUS_SUCCESS
    assert result["removed"] is None


# ---------------------------------------------------------------------------
# PatchApplier
# ---------------------------------------------------------------------------

def _applier(repo, policy=None):
    if policy is None:
        policy = merge_sandbox_policy(default_sandbox_policy(repo), {
            "source_write_allowed": True,
            "allowlisted_write_paths": [".agentx-init/", "src/"],
        })
    return PatchApplier(repo, policy, "sess-applier", "gov-applier")


def test_applier_update(repo):
    applier = _applier(repo)
    action = PatchAction(
        action_id="act-upd",
        target_file="src/greeting.py",
        change_type=ACTION_UPDATE,
        old_text="def hello():\n    return 'hello'\n",
        new_text="def hello():\n    return 'hello world'\n",
    )
    result = applier.apply_action(action)
    assert result.status == "APPLIED"
    assert result.new_hash is not None
    assert (repo / "src" / "greeting.py").read_text() == (
        "def hello():\n    return 'hello world'\n"
    )


def test_applier_update_no_old_text_fails(repo):
    applier = _applier(repo)
    action = PatchAction(
        action_id="act-no-old",
        target_file="src/greeting.py",
        change_type=ACTION_UPDATE,
        old_text="",
        new_text="new content",
    )
    result = applier.apply_action(action)
    assert result.status == "FAILED"


def test_applier_update_file_not_found(repo):
    applier = _applier(repo)
    action = PatchAction(
        action_id="act-missing",
        target_file="src/nonexistent.py",
        change_type=ACTION_UPDATE,
        old_text="anything",
        new_text="new content",
    )
    result = applier.apply_action(action)
    assert result.status == "FAILED"


def test_applier_create(repo):
    applier = _applier(repo)
    action = PatchAction(
        action_id="act-create",
        target_file="src/new_file.txt",
        change_type=ACTION_CREATE,
        new_text="brand new file",
    )
    result = applier.apply_action(action)
    assert result.status == "APPLIED"
    assert (repo / "src" / "new_file.txt").read_text() == "brand new file"


def test_applier_delete(repo):
    applier = _applier(repo)
    target = "src/to_delete.txt"
    (repo / target).write_text("will be deleted")
    action = PatchAction(
        action_id="act-del",
        target_file=target,
        change_type=ACTION_DELETE,
    )
    result = applier.apply_action(action)
    assert result.status == "APPLIED"
    assert not (repo / target).exists()


def test_applier_delete_file_not_found(repo):
    applier = _applier(repo)
    action = PatchAction(
        action_id="act-del-missing",
        target_file="src/ghost.txt",
        change_type=ACTION_DELETE,
    )
    result = applier.apply_action(action)
    assert result.status == "FAILED"


def test_applier_unknown_change_type(repo):
    applier = _applier(repo)
    action = PatchAction(
        action_id="act-unknown",
        target_file="src/f.py",
        change_type="REFACTOR",
    )
    result = applier.apply_action(action)
    assert result.status == "FAILED"


# ---------------------------------------------------------------------------
# ImplementationSession — lifecycle
# ---------------------------------------------------------------------------

def test_session_load_proposal(repo, source_write_policy):
    sess = ImplementationSession(repo, source_write_policy)
    proposal = {
        "actions": [
            {"target_file": "src/greeting.py", "change_type": "UPDATE",
             "old_text": "def hello():\n    return 'hello'\n",
             "new_text": "def hello():\n    return 'hi'\n"},
            {"target_file": "src/config.txt", "change_type": "UPDATE",
             "old_text": "setting=old\n", "new_text": "setting=new\n"},
        ]
    }
    sess.load_proposal(proposal)
    assert sess.session.status.current == SESSION_PROPOSAL_LOADED
    assert len(sess.session.actions) == 2
    assert "src/greeting.py" in sess.session.target_paths
    assert "src/config.txt" in sess.session.target_paths


def test_session_load_proposal_accepts_proposed_changes_key(repo, source_write_policy):
    sess = ImplementationSession(repo, source_write_policy)
    proposal = {
        "proposed_changes": [
            {"file": "src/greeting.py", "type": "UPDATE",
             "old_text": "def hello():", "new_text": "def hi():"},
        ]
    }
    sess.load_proposal(proposal)
    assert sess.session.status.current == SESSION_PROPOSAL_LOADED
    assert sess.session.actions[0].target_file == "src/greeting.py"


def test_session_check_governance_missing_id(repo, source_write_policy):
    sess = ImplementationSession(repo, source_write_policy,
                                  governance_decision_id="")
    proposal = {"actions": [{"target_file": "src/greeting.py"}]}
    sess.load_proposal(proposal)
    decision = sess.check_governance()
    assert decision.decision == DECISION_BLOCK
    assert "Governance decision ID is required" in decision.reason


def test_session_check_governance_passes(repo, source_write_policy):
    sess = ImplementationSession(repo, source_write_policy,
                                  governance_decision_id="gov-valid")
    proposal = {"actions": [{"target_file": "src/greeting.py"}]}
    sess.load_proposal(proposal)
    decision = sess.check_governance()
    assert decision.decision == DECISION_ALLOW
    assert sess.session.status.current == SESSION_GOVERNANCE_CHECKED


def test_session_snapshot_before_apply(repo, source_write_policy):
    sess = ImplementationSession(repo, source_write_policy,
                                  governance_decision_id="gov-001")
    proposal = {"actions": [{"target_file": "src/greeting.py",
                              "old_text": "def hello():\n    return 'hello'\n",
                              "new_text": "def hello():\n    return 'hi'\n"}]}
    sess.load_proposal(proposal)
    sess.check_governance()
    sess.snapshot_before_apply()
    assert len(sess.session.rollback_snapshot_paths) == 1
    snap_path = Path(sess.session.rollback_snapshot_paths[0])
    assert snap_path.exists()
    assert "src__greeting.py.bak" in snap_path.name


@pytest.fixture
def lifecycle_policy(repo):
    return merge_sandbox_policy(default_sandbox_policy(repo), {
        "source_write_allowed": True,
        "shell_allowed": True,
        "allowlisted_commands": [["python3", "-c"]],
        "allowlisted_write_paths": [".agentx-init/", "src/"],
    })


def test_session_full_accept_lifecycle(repo, lifecycle_policy):
    sess = ImplementationSession(repo, lifecycle_policy,
                                  governance_decision_id="gov-lifecycle")
    proposal = {"actions": [{"target_file": "src/greeting.py",
                              "change_type": "UPDATE",
                              "old_text": "def hello():\n    return 'hello'\n",
                              "new_text": "def hello():\n    return 'hi'\n"}]}
    sess.load_proposal(proposal)
    assert sess.session.status.current == SESSION_PROPOSAL_LOADED

    decision = sess.check_governance()
    assert decision.decision == DECISION_ALLOW
    assert sess.session.status.current == SESSION_GOVERNANCE_CHECKED

    sess.snapshot_before_apply()

    sess.apply_patch()
    assert sess.session.status.current == SESSION_PATCH_APPLIED
    assert (repo / "src" / "greeting.py").read_text() == (
        "def hello():\n    return 'hi'\n"
    )

    result = sess.validate([["python3", "-c", "import sys; sys.exit(0)"]])
    assert sess.session.status.current == SESSION_VALIDATED
    assert sess.session.validation_result["all_passed"]

    sess.accept()
    assert sess.session.status.current == SESSION_ACCEPTED

    evidence_path = repo / ".agentx-init" / "implementation" / "implementation_evidence.jsonl"
    assert evidence_path.exists()
    lines = evidence_path.read_text().strip().split("\n")
    assert any("SESSION_ACCEPTED" in l for l in lines)


def test_session_rollback_path(repo, lifecycle_policy):
    sess = ImplementationSession(repo, lifecycle_policy,
                                  governance_decision_id="gov-rollback")
    original_content = (repo / "src" / "greeting.py").read_text()
    proposal = {"actions": [{"target_file": "src/greeting.py",
                              "change_type": "UPDATE",
                              "old_text": "def hello():\n    return 'hello'\n",
                              "new_text": "def hello():\n    return 'modified'\n"}]}
    sess.load_proposal(proposal)
    sess.check_governance()
    sess.snapshot_before_apply()
    sess.apply_patch()
    assert (repo / "src" / "greeting.py").read_text() != original_content

    result = sess.validate([["python3", "-c", "import sys; sys.exit(1)"]])
    assert sess.session.status.current == SESSION_FAILED
    assert not sess.session.validation_result["all_passed"]

    sess.rollback()
    assert sess.session.status.current == SESSION_ROLLED_BACK
    assert (repo / "src" / "greeting.py").read_text() == original_content


def test_session_fail(repo, source_write_policy):
    sess = ImplementationSession(repo, source_write_policy,
                                  governance_decision_id="gov-fail")
    sess.load_proposal({"actions": [{"target_file": "src/greeting.py"}]})
    sess.fail("Something went wrong")
    assert sess.session.status.current == SESSION_FAILED
    assert any("Something went wrong" in e for e in sess.session.errors)


def test_session_writes_session_file(repo, source_write_policy):
    sess = ImplementationSession(repo, source_write_policy,
                                  governance_decision_id="gov-write")
    sess.load_proposal({"actions": [{"target_file": "src/greeting.py",
                                      "change_type": "UPDATE",
                                      "old_text": "old",
                                      "new_text": "new"}]})
    sess.fail("intentional")
    session_file = repo / ".agentx-init" / "implementation" / "sessions" / f"{sess.session_id}.json"
    assert session_file.exists()
    data = json.loads(session_file.read_text())
    assert data["session_id"] == sess.session_id


# ---------------------------------------------------------------------------
# ImplementationEvidenceWriter
# ---------------------------------------------------------------------------

def test_evidence_writer_write_evidence(repo):
    writer = ImplementationEvidenceWriter(repo)
    ev = ImplementationEvidence(
        evidence_id="ev-test",
        session_id="sess-ev",
        event_type="TEST",
        summary="test write",
    )
    result = writer.write_evidence(ev)
    assert result["status"] == "APPENDED"
    evidence_path = repo / ".agentx-init" / "implementation" / "implementation_evidence.jsonl"
    assert evidence_path.exists()
    lines = evidence_path.read_text().strip().split("\n")
    assert any("ev-test" in l for l in lines)


def test_evidence_writer_write_evidence_appends(repo):
    writer = ImplementationEvidenceWriter(repo)
    writer.write_evidence(ImplementationEvidence(
        evidence_id="ev-1", session_id="s1", event_type="T1", summary="s1",
    ))
    writer.write_evidence(ImplementationEvidence(
        evidence_id="ev-2", session_id="s2", event_type="T2", summary="s2",
    ))
    evidence_path = repo / ".agentx-init" / "implementation" / "implementation_evidence.jsonl"
    lines = [l for l in evidence_path.read_text().strip().split("\n") if l]
    assert len(lines) == 2


def test_evidence_writer_write_latest_session(repo):
    writer = ImplementationEvidenceWriter(repo)
    result = writer.write_latest_session({
        "session_id": "sess-latest",
        "status": "ACCEPTED",
    })
    assert result["status"] == "WRITTEN"
    latest_path = repo / ".agentx-init" / "implementation" / "implementation_latest.json"
    assert latest_path.exists()
    data = json.loads(latest_path.read_text())
    assert data["session_id"] == "sess-latest"


# ---------------------------------------------------------------------------
# ImplementationValidationGate
# ---------------------------------------------------------------------------

def test_validation_gate_all_passed_empty():
    gate = ImplementationValidationGate(Path("/tmp"), default_sandbox_policy(Path("/tmp")))
    assert gate.all_passed([])


def test_validation_gate_all_passed_true():
    gate = ImplementationValidationGate(Path("/tmp"), default_sandbox_policy(Path("/tmp")))
    results = [
        {"command": ["echo", "ok"], "status": "PASS"},
        {"command": ["true"], "status": "PASS"},
    ]
    assert gate.all_passed(results)


def test_validation_gate_all_passed_false():
    gate = ImplementationValidationGate(Path("/tmp"), default_sandbox_policy(Path("/tmp")))
    results = [
        {"command": ["true"], "status": "PASS"},
        {"command": ["false"], "status": "FAIL"},
    ]
    assert not gate.all_passed(results)


@pytest.fixture
def permissive_policy(repo):
    return merge_sandbox_policy(default_sandbox_policy(repo), {
        "shell_allowed": True,
        "allowlisted_commands": [["echo"], ["python3", "-c"]],
    })


def test_validation_gate_run_allowed_command(repo, permissive_policy):
    gate = ImplementationValidationGate(repo, permissive_policy)
    results = gate.run_validation_commands([["echo", "hello"]])
    assert len(results) == 1
    assert results[0]["status"] == "PASS"


def test_validation_gate_run_blocked_command(repo, default_policy):
    gate = ImplementationValidationGate(repo, default_policy)
    results = gate.run_validation_commands([["bash", "-c", "echo hi"]])
    assert len(results) == 1
    assert results[0]["status"] == "BLOCKED"
    assert "subprocess" in results[0]["reason"].lower()


def test_validation_gate_run_failing_command(repo, permissive_policy):
    gate = ImplementationValidationGate(repo, permissive_policy)
    results = gate.run_validation_commands([["python3", "-c", "import sys; sys.exit(1)"]])
    assert len(results) == 1
    assert results[0]["status"] == "FAIL"


# ---------------------------------------------------------------------------
# Negative / edge cases
# ---------------------------------------------------------------------------

def test_session_blocks_writes_to_L0_via_full_lifecycle(repo):
    policy = merge_sandbox_policy(default_sandbox_policy(repo), {
        "source_write_allowed": True,
    })
    sess = ImplementationSession(repo, policy, governance_decision_id="gov-l0")
    proposal = {"actions": [{"target_file": "L0/protected.py",
                              "change_type": "UPDATE",
                              "old_text": "original",
                              "new_text": "modified"}]}
    sess.load_proposal(proposal)
    sess.check_governance()
    sess.apply_patch()
    for act in sess.session.actions:
        assert act.status == "BLOCKED"
    # original content preserved
    assert (repo / "L0" / "protected.py").read_text() == "original l0 content"


def test_rollback_manager_snapshot_creates_dir(repo):
    manager = RollbackManager(repo)
    snap = manager.snapshot_file("src/greeting.py", "sess-dir-test")
    assert Path(snap.snapshot_path).parent.exists()
    Path(snap.snapshot_path).unlink(missing_ok=True)


def test_implementation_session_id_property(repo, source_write_policy):
    sess = ImplementationSession(repo, source_write_policy, session_id="my-sess-id")
    assert sess.session_id == "my-sess-id"
